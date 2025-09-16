from __future__ import annotations

from typing import TYPE_CHECKING

from abc import abstractmethod
from collections.abc import Callable, Iterator, Mapping
from copy import copy
from dataclasses import dataclass, field
from functools import cached_property

# os.truncate was unused; removed to clean imports
from types import MappingProxyType
from typing import Any, Iterable, Literal, Self

from typeguard import TypeCheckError, check_type

from reactk.model2.prop_model.common import DiffMode
from reactk.model2.util.missing import MISSING_TYPE, MISSING

if TYPE_CHECKING:
    from reactk.model.trace.key_tools import Display
    from reactk.model.trace.render_trace import RenderTrace
from reactk.model2.prop_model.common import (
    _IS_REQUIRED_TYPE,
    IS_REQUIRED,
    Converter,
    KeyedValues,
)
from reactk.model2.prop_model.v_mapping import (
    VMappingBase,
    deep_merge,
)
from reactk.model2.util.str import join_truncate


type SomeProp = "Prop | PropSchema"


class PropLike:
    name: str
    repr: DiffMode
    metadata: Mapping[str, Any]
    computed_name: str | None = None
    path: tuple[str, ...]

    @property
    def fqn(self) -> str:
        return ".".join(self.path + (self.name,)) if self.path else self.name

    @property
    @abstractmethod
    def is_required(self) -> bool: ...

    @abstractmethod
    def assert_valid(self, input: Any) -> None: ...

    def is_valid(self, input: Any) -> bool:
        try:
            self.assert_valid(input)
            return True
        except ValueError as e:
            return False

    def __hash__(self) -> int:
        return super().__hash__()


class PropSchema(VMappingBase[str, "SomeProp"], PropLike):

    def __init__(
        self,
        path: tuple[str, ...],
        name: str,
        props: "PropSchema.Input" = (),
        repr: DiffMode = "recursive",
        computed_name: str | None = None,
        metadata: Mapping[str, Any] = {},
    ):
        self.path = path
        self.name = name
        self.repr = repr
        self.computed_name = computed_name
        self.metadata = metadata
        self._props = self._to_dict(props)

    def _get_key(self, value: "SomeProp") -> str:
        return value.name

    @property
    def is_required(self) -> bool:
        return all(prop.is_required for prop in self)

    @property
    def _debug(self):
        return [str(x) if isinstance(x, Prop) else x._debug for x in self]

    def _with_props(self, new_props: "PropSchema.Input") -> Self:
        """Return a new instance of the same concrete class with the given values."""
        copyed = copy(self)
        copyed._props = self._to_dict(new_props)
        return copyed

    def __iter__(self) -> Iterator["SomeProp"]:
        return iter(self._props.values())

    def __len__(self) -> int:
        return len(self._props)

    def __getitem__(self, key: str) -> "SomeProp":
        return self._props[key]

    def assert_valid(self, input: Any) -> None:
        if not isinstance(input, Mapping):
            raise ValueError(
                f"Input for {self.name} must be a mapping, got {type(input)}"
            )
        for prop in self:
            if not prop.name in input:
                if prop.is_required:
                    raise ValueError(
                        f"Missing required prop {prop.name} in {self.name}"
                    )
                continue
            prop.is_valid(input[prop.name])
        extra_props = set(input.keys()) - {prop.name for prop in self}
        if extra_props:
            joined = ", ".join(extra_props)
            raise ValueError(f"Extra props {joined} in {self.name}")

    def update(self, other: "PropSchema.Input") -> "PropSchema":
        merged_props = deep_merge(self._props, self._to_dict(other))
        return self._with_props(merged_props)

    def __str__(self) -> str:
        return f"⟦{self.fqn}: {join_truncate(self, 5)}⟧"


@dataclass(kw_only=True, eq=False)
class Prop[T](PropLike):
    converter: Converter[T] | None = field(default=None)
    subsection: str | None = field(default=None)
    no_value: T | None = field(default=None)
    value_type: type[T]
    name: str
    repr: DiffMode = field(default="recursive")
    metadata: Mapping[str, Any] = field(default=MappingProxyType({}))
    computed_name: str | None = field(default=None)
    path: tuple[str, ...]

    def __call__(self, value: T) -> "PropScalar[T]":
        return self.to_value(value)

    @property
    def is_required(self) -> bool:
        return self.no_value is not None

    def __str__(self) -> str:
        return f"（{self.fqn} :: {self.value_type}）"

    def to_value(
        self, value: T | None = None, *, old: T | None = None
    ) -> PropScalar[T]:

        return PropScalar(prop=self, value=value, old=old)

    def assert_valid(self, input: Any):
        try:
            if input is None and self.is_required:
                raise ValueError(f"Value for {self.fqn} is required")
            if self.value_type is None:
                return
            if self.value_type is not None:
                if self.value_type is float and isinstance(input, int):
                    input = float(input)  # type: ignore
                check_type(input, self.value_type)
        except TypeCheckError as e:
            raise ValueError(f"Typecheck failed in {self.fqn}: {e.args[0]}") from e


def format_value(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


@dataclass
class PropScalar[T]:
    __match_args__ = ("value", "prop")
    prop: Prop[T]
    value: T | None = field(default=None)
    old: T | None = field(default=None)

    def __post_init__(self):
        if self.prop.is_required and self.value is None:
            raise ValueError(f"Value for required prop {self.prop.name} is missing")

    @property
    def fqn(self) -> str:
        return self.prop.fqn

    @property
    def computed_name(self) -> str:
        return self.prop.computed_name or self.prop.name

    def __str__(self) -> str:
        return f"（{self.fqn} :: {self.prop.value_type} ➔ {str(self.value)}）"

    @property
    def is_missing(self) -> bool:
        return self.value is MISSING

    def compute(self) -> T:
        v = self.prop.no_value if self.is_missing else self.value
        v_: T = v  # type: ignore
        v_ = self.prop.converter(v_) if self.prop.converter else v_
        return v_

    def __hash__(self) -> int:
        return hash((type(self), self.prop, self.value))

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, PropScalar)
            and self.prop == other.prop
            and self.value == other.value
        )

    @property
    def name(self) -> str:
        return self.prop.name

    def update(self, value: T) -> "PropScalar[T]":

        return PropScalar(
            prop=self.prop, value=value, old=self.value if self.value else None
        )


class PropVector(VMappingBase[str, "SomePropValue"]):
    @property
    def name(self) -> str:
        return self.schema.name

    def __init__(
        self,
        schema: PropSchema,
        values: KeyedValues,
        old: KeyedValues | None = None,
    ):
        self.schema = schema
        self._values = values
        self._old = old
        self.schema.assert_valid(values)

    @property
    def fqn(self) -> str:
        return self.schema.fqn

    @property
    def computed_name(self) -> str:
        return self.schema.computed_name or self.schema.name

    def compute(self) -> "PDiff":
        result = {}

        def _get_or_create_section(name: str | None) -> dict[str, Any]:
            if name is None:
                return result
            if name not in result:
                result[name] = {}

            return result[name]

        for pv in self:
            match pv:
                case PropScalar() as v:
                    v_ = v.compute()
                    section = _get_or_create_section(v.prop.subsection)
                    section[v.computed_name] = v_
                case PropVector() as bv:
                    result.update({bv.computed_name: bv.compute()})
        return PDiff(diff=result, source=self)

    def get_pv(self, key: str) -> PropScalar[Any]:
        match self[key]:
            case PropScalar(x, _) as p:
                return p
            case _:
                raise ValueError(f"Key {key} is not a Prop")

    def get_pbv(self, key: str) -> "PropVector":
        match self[key]:
            case PropVector() as pb:
                return pb
            case _:
                raise ValueError(f"Key {key} is not a PropBlock")

    def __iter__(self) -> Iterator["PropScalar | PropVector"]:
        for prop in self.schema:
            yield self._wrap(prop)

    def __len__(self) -> int:
        return len(self.schema)

    def _wrap(self, prop: SomeProp) -> "SomePropValue":
        old_value = self._old.get(prop.name) if self._old else None
        match prop:
            case Prop() as p:
                return p.to_value(
                    value=self._values.get(p.name, p.no_value), old=old_value
                )

            case PropSchema() as pb:
                return PropVector(
                    schema=pb, values=self._values.get(pb.name, {}), old=old_value
                )
            case _:
                raise ValueError(f"Invalid prop type: {type(prop)}")

    def __getitem__(self, key: str) -> "PropScalar | PropVector":
        schema = self.schema[key]
        return self._wrap(schema)

    def __str__(self) -> str:
        return f"⟪{self.fqn}: {join_truncate(self, 5)}⟫"

    @property
    def _debug(self):
        return [str(x) if isinstance(x, PropScalar) else x._debug for x in self]

    def _get_key(self, value: "SomePropValue") -> str:
        return value.name

    def update(self, overrides: KeyedValues) -> "PropVector":
        new_values = self._to_dict(self)
        for x in self:
            other = overrides.get(x.name)
            if other is None:
                continue
            cur = new_values[x.name]
            cur = cur.update(other)
            new_values[x.name] = cur
        return PropVector(schema=self.schema, values=new_values, old=self._values)

    def diff(self, other: "PropVector | KeyedValues") -> "PDiff":
        if not isinstance(other, PropVector):
            other = PropVector(schema=self.schema, values=other)
        self.schema.assert_valid(other._values)
        out = {}
        for k in {*self.keys(), *other.keys()}:
            if k not in self:
                out[k] = other[k]
            elif k not in other:
                continue
            my_prop = self[k]
            match my_prop:
                case PropScalar():
                    if my_prop != other[k]:
                        out[k] = other[k]
                case PropVector():
                    other_prop = other[k]
                    if not isinstance(other_prop, PropVector):
                        raise ValueError(
                            f"Cannot diff mapping with non-mapping at {my_prop}"
                        )
                    if my_prop.schema.repr == "recursive":
                        result = my_prop.diff(other_prop)
                        if result:
                            out[k] = result
                    else:
                        if my_prop != other[k]:
                            out[k] = other[k]

        return PDiff(diff=out, source=other)


@dataclass
class PDiff:
    diff: KeyedValues
    source: PropVector

    def __bool__(self) -> bool:
        return bool(self.diff)


type SomePropValue = "PropScalar | PropVector"
