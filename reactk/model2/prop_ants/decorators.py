from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Concatenate,
    Iterable,
    Mapping,
    Protocol,
    Self,
    overload,
)

from reactk.model2.prop_ants.prop_meta import prop_meta, schema_meta

if TYPE_CHECKING:
    from reactk.model2.prop_model.prop import Prop_Schema, Prop_Mapping
    from reactk.model2.prop_model.common import KeyedValues
    from reactk.model2.prop_ants.prop_meta import some_meta


class _HasMerge(Protocol):
    __PROPS__: ClassVar["Prop_Schema"]
    __PROP_VALUES__: "Prop_Mapping"

    def __merge__(self, other: "KeyedValues") -> Self: ...


@dataclass
class MethodSetterTransformer:
    @property
    @abstractmethod
    def self_meta(self) -> "some_meta": ...

    def _transform(self, f: Callable) -> Callable:
        def wrapper(self: _HasMerge, input: "KeyedValues") -> Self:
            if not isinstance(input, Mapping):
                raise TypeError(
                    f"Schema setter method {f.__name__} must return a Mapping, got {type(input)}"
                )
            return self.__merge__({f.__name__: input})  # type: ignore

        return wrapper

    @overload
    def __call__[**P, R: _HasMerge](
        self, f: Callable[Concatenate[R, P], None]
    ) -> Callable[Concatenate[R, P], R]: ...

    @overload
    def __call__[**P, R: _HasMerge](
        self,
    ) -> Callable[
        [Callable[Concatenate[R, P], Any]], Callable[Concatenate[R, P], R]
    ]: ...

    def __call__(self, f: Callable[..., Any] | None = None) -> Any:

        def apply(f: Callable) -> Any:
            transformed = self._transform(f)
            # perform runtime imports here to avoid circular imports at module import time
            from reactk.model2.ants.readers import OrigAccessor
            from reactk.model2.prop_ants.create_props import MetaAccessor

            OrigAccessor(transformed).set(f)
            MetaAccessor(f).set(self.self_meta)
            return transformed

        return apply(f) if f else apply


@dataclass(kw_only=True)
class schema_setter(MethodSetterTransformer, schema_meta):
    @property
    def self_meta(self) -> Any:
        return self


@dataclass(kw_only=True)
class prop_setter(MethodSetterTransformer, prop_meta):
    @property
    def self_meta(self) -> Any:
        return self


@dataclass
class _getter[X]:
    prop_name: str

    def __get__(self, instance: Any, owner) -> X:
        if instance is None:
            return self  # type: ignore
        v = instance.__PROP_VALUES__[self.prop_name].compute()
        return v  # type: ignore


@dataclass
class prop_getter:
    name: str | None = field(default=None)

    def __call__[R](self, f: Callable[[Any], R]):
        prop_name = self.name or f.__name__

        return _getter[R](prop_name)


class HasChildren[Child](_HasMerge):

    def __getitem__(self, children: Iterable[Child]) -> Self:
        return self.__merge__({"__CHILDREN__": children})
