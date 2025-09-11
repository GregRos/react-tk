from abc import abstractmethod
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Concatenate,
    Mapping,
    Protocol,
    Self,
    overload,
)

from reactk.model2.annotations import OrigAccessor
from reactk.model2.prop_model.common import IS_REQUIRED, Converter, DiffMode

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


@dataclass(kw_only=True)
class prop_meta(common_meta):
    no_value: Any = IS_REQUIRED
    converter: Converter[Any] | None = None


@dataclass(kw_only=True)
class schema_meta(common_meta):
    pass


class _HasMerge(Protocol):
    __PROPS__: ClassVar["PropBlock"]
    __VALUES__: "PropBlockValues"

    def __merge__(self, other: Mapping[str, Any]) -> Any: ...


class MethodSetterTransformer:
    def _transform(self, f: Callable) -> Callable:
        def wrapper(self: _HasMerge, input: Mapping[str, Any]) -> Self:
            if not isinstance(input, Mapping):
                raise TypeError(
                    f"Schema setter method {f.__name__} must return a Mapping, got {type(input)}"
                )
            return self.__merge__({f.__name__: input})

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
            return transformed

        return apply(f) if f else apply


@dataclass(kw_only=True)
class schema_setter(schema_meta, MethodSetterTransformer):
    pass


@dataclass(kw_only=True)
class prop_setter(prop_meta, MethodSetterTransformer):
    pass


@dataclass
class prop_value_getter:
    name: str | None = field(default=None)

    def __call__[F: Callable[[_HasProps], Any]](self, f: F) -> F:
        prop_name = self.name or f.__name__

        def get_prop_value(self: _HasProps) -> Any:

            return

        return f


type some_meta = prop_meta | schema_meta
