from __future__ import annotations
from typing import TYPE_CHECKING
from expression import Nothing, Some, Option

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
from reactk.model2.util.maybe import MaybeOption, maybe_normalize
from reactk.model2.util.missing import MISSING_TYPE, MISSING

if TYPE_CHECKING:
    from reactk.model.trace.key_tools import Display
    from reactk.model.trace.render_trace import RenderTrace
from reactk.model2.prop_model.common import (
    Converter,
    KeyedValues,
)
from reactk.model2.prop_model.v_mapping import (
    VMappingBase,
    deep_merge,
)
from reactk.model2.util.str import join_truncate


type Prop_Any = "Prop | Prop_Schema"


class _Prop_Base:
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


class Prop_Schema(VMappingBase[str, "Prop_Any"], _Prop_Base):

    def __init__(
        self,
        path: tuple[str, ...],
        name: str,
        props: "Prop_Schema.Input" = (),
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

    def __call__(self, values: "KeyedValues" = MappingProxyType({})) -> "Prop_Mapping":
        return self.with_values(values)

    def with_values(
        self, values: "KeyedValues" = MappingProxyType({})
    ) -> "Prop_Mapping":
        return Prop_Mapping(self, values)

    def _get_key(self, value: "Prop_Any") -> str:
        return value.name

    @property
    def is_required(self) -> bool:
        return all(prop.is_required for prop in self)

    @property
    def _debug(self):
        return [str(x) if isinstance(x, Prop) else x._debug for x in self]

    def _with_props(self, new_props: "Prop_Schema.Input") -> Self:
        """Return a new instance of the same concrete class with the given values."""
        copyed = copy(self)
        copyed._props = self._to_dict(new_props)
        return copyed

    def __iter__(self) -> Iterator["Prop_Any"]:
        return iter(self._props.values())

    def __len__(self) -> int:
        return len(self._props)

    def __getitem__(self, key: str) -> "Prop_Any":
        return self._props[key]

    def assert_valid(self, input: KeyedValues) -> None:
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
            prop.assert_valid(input[prop.name])
        extra_props = set(input.keys()) - {prop.name for prop in self}
        if extra_props:
            joined = ", ".join(extra_props)
            raise ValueError(f"Extra props {joined} in {self.name}")

    def update(self, other: "Prop_Schema.Input") -> "Prop_Schema":
        merged_props = deep_merge(self._props, self._to_dict(other))
        return self._with_props(merged_props)

    def __str__(self) -> str:
        return f"⟦{self.fqn}: {join_truncate(self, 5)}⟧"


@dataclass(kw_only=True, eq=False)
class Prop[T](_Prop_Base):
    converter: Converter[T] | None = field(default=None)
    subsection: str | None = field(default=None)
    no_value: Option[T] = field(default=Nothing)
    value_type: type[T]
    name: str
    repr: DiffMode = field(default="recursive")
    metadata: Mapping[str, Any] = field(default=MappingProxyType({}))
    computed_name: str | None = field(default=None)
    path: tuple[str, ...]

    def __call__(self, value: MaybeOption[T] = Nothing) -> "Prop_Value[T]":
        return self.to_value(value)

    @property
    def is_required(self) -> bool:
        return self.no_value is Nothing

    def __str__(self) -> str:
        return f"（{self.fqn} :: {self.value_type}）"

    def to_value(
        self, value: MaybeOption[T] = Nothing, *, old: MaybeOption[T] = Nothing
    ) -> Prop_Value[T]:
        return Prop_Value(
            prop=self, value=maybe_normalize(value), old=maybe_normalize(old)
        )

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
class Prop_Value[T]:
    __match_args__ = ("value", "prop")
    prop: Prop[T]
    value: Option[T] = field(default=Nothing)
    old: Option[T] = field(default=Nothing)

    def __post_init__(self):
        if self.prop.is_required and self.value is Nothing:
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
        return self.value is Nothing

    def compute(self) -> T:
        v = maybe_normalize(self.prop.no_value) if self.is_missing else self.value
        v_: T = v.value  # type: ignore
        v_ = self.prop.converter(v_) if self.prop.converter else v_
        return v_

    def __hash__(self) -> int:
        return hash((type(self), self.prop, self.value))

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Prop_Value)
            and self.prop == other.prop
            and self.value == other.value
        )

    @property
    def name(self) -> str:
        return self.prop.name

    def update(self, value: T) -> "Prop_Value[T]":

        return Prop_Value(prop=self.prop, value=Some(value), old=self.value)


class Prop_Mapping(VMappingBase[str, "SomePropValue"]):
    @property
    def name(self) -> str:
        return self.prop.name

    def __init__(
        self,
        prop: Prop_Schema,
        value: KeyedValues,
        old: KeyedValues | None = None,
    ):
        self.prop = prop
        self._values = value
        self._old = old
        self.prop.assert_valid(value)

    @property
    def fqn(self) -> str:
        return self.prop.fqn

    @property
    def computed_name(self) -> str:
        return self.prop.computed_name or self.prop.name

    def compute(self) -> "Prop_ComputedMapping":
        result = {}

        def _get_or_create_section(name: str | None) -> dict[str, Any]:
            if name is None:
                return result
            if name not in result:
                result[name] = {}

            return result[name]

        for pv in self:
            match pv:
                case Prop_Value() as v:
                    v_ = v.compute()
                    section = _get_or_create_section(v.prop.subsection)
                    section[v.computed_name] = v_
                case Prop_Mapping() as bv:
                    result.update({bv.computed_name: bv.compute()})
        return Prop_ComputedMapping(diff=result, source=self)

    def get_pv(self, key: str) -> Prop_Value[Any]:
        match self[key]:
            case Prop_Value(x, _) as p:
                return p
            case _:
                raise ValueError(f"Key {key} is not a Prop")

    def get_pbv(self, key: str) -> "Prop_Mapping":
        match self[key]:
            case Prop_Mapping() as pb:
                return pb
            case _:
                raise ValueError(f"Key {key} is not a PropBlock")

    def __iter__(self) -> Iterator["Prop_Value | Prop_Mapping"]:
        for prop in self.prop:
            yield self._wrap(prop)

    def __len__(self) -> int:
        return len(self.prop)

    def _wrap(self, prop: Prop_Any) -> "SomePropValue":
        old_value = self._old.get(prop.name) if self._old else None
        match prop:
            case Prop() as p:
                return p.to_value(
                    value=self._values.get(p.name, Nothing), old=old_value
                )

            case Prop_Schema() as pb:
                return Prop_Mapping(
                    prop=pb, value=self._values.get(pb.name, {}), old=old_value
                )
            case _:
                raise ValueError(f"Invalid prop type: {type(prop)}")

    def __getitem__(self, key: str) -> "Prop_Value | Prop_Mapping":
        schema = self.prop[key]
        return self._wrap(schema)

    def __str__(self) -> str:
        return f"⟪{self.fqn}: {join_truncate(self, 5)}⟫"

    @property
    def _debug(self):
        return [str(x) if isinstance(x, Prop_Value) else x._debug for x in self]

    def _get_key(self, value: "SomePropValue") -> str:
        return value.name

    @classmethod
    def _from_mapping(
        cls,
        schema: Prop_Schema,
        mapping: Mapping[str, "SomePropValue"],
        old: KeyedValues = MappingProxyType({}),
    ) -> "Prop_Mapping":
        kvs = {}
        for prop in mapping.values():
            match prop:
                case Prop_Value() as pv:
                    kvs[pv.prop.name] = pv.value
                case Prop_Mapping() as pm:
                    kvs[pm.prop.name] = pm._values
                case _:
                    raise ValueError(f"Invalid prop type: {type(prop)}")
        return Prop_Mapping(prop=schema, value=kvs, old=old)

    def update(self, overrides: KeyedValues) -> "Prop_Mapping":
        new_values = deep_merge(self._values, overrides)
        self.prop.assert_valid(new_values)
        return Prop_Mapping(prop=self.prop, value=new_values, old=self._values)

    def diff(self, other: "Prop_Mapping | KeyedValues") -> "Prop_ComputedMapping":
        if not isinstance(other, Prop_Mapping):
            other = Prop_Mapping(prop=self.prop, value=other)
        self.prop.assert_valid(other._values)
        out = {}
        for k in {*self.keys(), *other.keys()}:
            if k not in self:
                out[k] = other[k]
            elif k not in other:
                continue
            match self[k], other[k]:
                case Prop_Value() as my_prop, Prop_Value() as other_prop:
                    if my_prop != other[k]:
                        out[my_prop.computed_name] = other_prop.compute()
                case Prop_Mapping() as my_prop, Prop_Mapping() as other_prop:
                    other_prop = other[k]
                    if not isinstance(other_prop, Prop_Mapping):
                        raise ValueError(
                            f"Cannot diff mapping with non-mapping at {my_prop}"
                        )
                    if my_prop.prop.repr == "recursive":
                        result = my_prop.diff(other_prop)
                        if result:
                            out[my_prop.computed_name] = result.diff
                    elif my_prop.prop.repr == "simple":
                        if my_prop != other[k]:
                            out[my_prop.computed_name] = other_prop._values
                    else:
                        continue
                case _:
                    raise ValueError(f"Cannot diff different prop types at {k}")
        return Prop_ComputedMapping(diff=out, source=other)


@dataclass
class Prop_ComputedMapping:
    diff: KeyedValues
    source: Prop_Mapping

    def __bool__(self) -> bool:
        return bool(self.diff)

    def __eq__(self, other: Any) -> bool:
        match other:
            case Prop_ComputedMapping() as o:
                return {
                    *self.diff.items(),
                } == {
                    *o.diff.items(),
                }
            case Mapping() as m:
                return {
                    *self.diff.items(),
                } == {
                    *m.items(),
                }
            case _:
                return False


type SomePropValue = "Prop_Value | Prop_Mapping"
