from dataclasses import dataclass
from typing import Any, Callable, Concatenate, overload

from reactk.model2.annotations import MetaAccessor, OrigAccessor
from reactk.model2.prop_model.common import IS_REQUIRED, Converter, DiffMode


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


@dataclass(kw_only=True)
class schema_setter(schema_meta):

    @overload
    def __call__[**P, R](
        self, f: Callable[Concatenate[R, P], None]
    ) -> Callable[Concatenate[R, P], R]: ...

    @overload
    def __call__[**P, R](
        self,
    ) -> Callable[
        [Callable[Concatenate[R, P], Any]], Callable[Concatenate[R, P], R]
    ]: ...

    def __call__[**P, R](self, f: Any | None = None) -> Any:

        def apply(f: Callable) -> Any:

            def set_section(self, **args: Any):
                if f.__name__ == "__init__":
                    self._props = get_or_init_prop_values(self, f).merge(args)
                    return
                return self._copy(**{f.__name__: args})

            OrigAccessor(set_section).set(f)
            return set_section

        return apply(f) if f else apply


type some_meta = prop_meta | schema_meta
