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

from reactk.model2.annotationss.annotations import OrigAccessor
from reactk.model2.prop_model.common import IS_REQUIRED, Converter, DiffMode
from reactk.model2.prop_annotations.prop_annotations import MetaAccessor

if TYPE_CHECKING:
    from reactk.model2.prop_model.prop import (
        Prop,
        PropBlock,
        SomeProp,
        PropBlockValues,
        SomePropValue,
    )


@dataclass(kw_only=True)
class common_meta:
    metadata: dict[str, Any] = {}
    repr: DiffMode = "recursive"
    name: str | None = None


@dataclass(kw_only=True)
class prop_meta(common_meta):
    subsection: str | None = None
    no_value: Any = IS_REQUIRED
    converter: Converter[Any] | None = None


@dataclass(kw_only=True)
class schema_meta(common_meta):
    pass


class _HasMerge(Protocol):
    __PROPS__: ClassVar["PropBlock"]
    __PROP_VALUES__: "PropBlockValues"

    def __merge__(self, other: Mapping[str, Any]) -> Self: ...


@dataclass
class MethodSetterTransformer:
    @property
    @abstractmethod
    def self_meta(self) -> "some_meta": ...

    def _transform(self, f: Callable) -> Callable:
        def wrapper(self: _HasMerge, input: Mapping[str, Any]) -> Self:
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
            OrigAccessor(transformed).set(f)
            MetaAccessor(f).set(self.self_meta)
            return transformed

        return apply(f) if f else apply


@dataclass(kw_only=True)
class schema_setter(schema_meta, MethodSetterTransformer):
    @property
    def self_meta(self) -> "some_meta":
        return self


@dataclass(kw_only=True)
class prop_setter(prop_meta, MethodSetterTransformer):
    @property
    def self_meta(self) -> "some_meta":
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


type some_meta = prop_meta | schema_meta


class HasChildren[Child](_HasMerge):
    def __getitem__(self, children: Iterable[Child]) -> Self:
        return self.__merge__({"__CHILDREN__": children})
