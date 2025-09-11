from abc import abstractmethod
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Iterable, Literal, Self

from typeguard import TypeCheckError, check_type

from reactk.model.props.prop import DiffMode
from reactk.model.trace.key_tools import Display
from reactk.model.trace.render_trace import RenderTrace
from reactk.model2.prop_model.common import _IS_REQUIRED_TYPE, IS_REQUIRED, Converter
from reactk.model2.v_mapping import VMapping, VMappingBase, VMappingInput, deep_merge


type SomeProp = "Prop | PropBlock"


class PropLike:
    name: str
    repr: DiffMode
    metadata: dict[str, Any]

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


class PropBlock(VMappingBase[str, "SomeProp"], PropLike):
    repr: DiffMode

    def __init__(
        self,
        name: str,
        props: "PropBlock.Input" = (),
        repr: DiffMode = "recursive",
        metadata: dict[str, Any] = {},
    ):
        self.name = name
        self.repr = repr
        self.metadata = metadata
        self._props = self._to_dict(props)

    def _get_key(self, value: "SomeProp") -> str:
        return value.name

    @property
    def is_required(self) -> bool:
        return all(prop.is_required for prop in self)

    def _with_props(self, new_props: "PropBlock.Input") -> Self:
        """Return a new instance of the same concrete class with the given values."""
        return type(self)(
            name=self.name, props=new_props, repr=self.repr, metadata=self.metadata
        )

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


@dataclass(kw_only=True)
class Prop[T](PropLike):
    converter: Converter[T] | None = field(default=None)
    no_value: T | _IS_REQUIRED_TYPE = field(default=IS_REQUIRED)
    value_type: type[T]
    name: str
    repr: DiffMode = field(default="recursive")
    metadata: dict[str, Any] = field(default_factory=dict)
    path: list[str] = field(default_factory=list)

    @property
    def is_required(self) -> bool:
        return self.no_value is _IS_REQUIRED_TYPE

    def is_valid(self, input: Any):
        try:
            self.assert_valid(input)
            return True
        except ValueError as e:
            return False

    @property
    def fqn(self) -> str:
        return ".".join(self.path + [self.name]) if self.path else self.name

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

    def __hash__(self) -> int:
        return super().__hash__()


def format_value(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


type SomePropValue = "PropValue | PropBlockValues"


@dataclass
class PropValue[T]:
    __match_args__ = ("value", "prop")
    prop: Prop[T]
    value: T
    old: "PropValue[T] | None" = None

    def __repr__(self) -> str:
        match self.prop.repr:
            case "none":
                return ""
            case "simple":
                return f"{self.prop.name}={self.value.__class__.__name__}"
            case "recursive":
                return f"{self.prop.name}={format_value(self.value)}"
            case _:
                raise ValueError(f"Invalid repr mode: {self.prop.repr}")

    def compute(self) -> T:
        v = self.value or self.prop.no_value
        if v is IS_REQUIRED:
            raise ValueError(f"Value for {self.prop.name} is required")
        v_: T = v  # type: ignore
        v_ = self.prop.converter(v_) if self.prop.converter else v_
        return v_

    def __hash__(self) -> int:
        return hash((type(self), self.prop, self.value))

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, PropValue)
            and self.prop == other.prop
            and self.value == other.value
        )

    @property
    def name(self) -> str:
        return self.prop.name

    def update(self, value: T) -> "PropValue[T]":
        return PropValue(prop=self.prop, value=value, old=self)


class PropBlockValues(VMappingBase[str, "SomePropValue"]):
    @property
    def name(self) -> str:
        return self.schema.name

    def __init__(
        self,
        schema: PropBlock,
        values: Mapping[str, Any],
        old: Mapping[str, Any] | None = None,
    ):
        self.schema = schema
        self._values = values
        self._old = old
        self.schema.assert_valid(values)

    def compute(self) -> Mapping[str, Any]:
        result = {}
        for pv in self:
            match pv:
                case PropValue() as v:
                    v_ = v.compute()
                    result[v.name] = v_
                case PropBlockValues() as bv:
                    result.update(bv.compute())
        return result

    def get_pv(self, key: str) -> PropValue[Any]:
        match self[key]:
            case PropValue(x, _) as p:
                return p
            case _:
                raise ValueError(f"Key {key} is not a Prop")

    def get_pbv(self, key: str) -> "PropBlockValues":
        match self[key]:
            case PropBlockValues() as pb:
                return pb
            case _:
                raise ValueError(f"Key {key} is not a PropBlock")

    def __iter__(self) -> Iterator["PropValue | PropBlockValues"]:
        for prop in self.schema:
            yield self._wrap(prop)

    def __len__(self) -> int:
        return len(self.schema)

    def _wrap(self, prop: SomeProp) -> SomePropValue:
        old_value = self._old.get(prop.name) if self._old else None
        match prop:
            case Prop() as p:
                return PropValue(
                    prop=p, value=self._values.get(p.name, p.no_value), old=old_value
                )
            case PropBlock() as pb:
                return PropBlockValues(
                    schema=pb, values=self._values.get(pb.name, {}), old=old_value
                )
            case _:
                raise ValueError(f"Invalid prop type: {type(prop)}")

    def __getitem__(self, key: str) -> "PropValue | PropBlockValues":
        schema = self.schema[key]
        return self._wrap(schema)

    def _get_key(self, value: "SomePropValue") -> str:
        return value.name

    def update(self, overrides: Mapping[str, Any]) -> "PropBlockValues":
        new_values = deep_merge(self._values, overrides)
        return PropBlockValues(schema=self.schema, values=new_values, old=self._values)
