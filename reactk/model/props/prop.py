from dataclasses import dataclass, field
from typeguard import TypeCheckError, check_type
from copy import copy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Concatenate,
    Literal,
    Self,
    Type,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    overload,
    override,
)

from reactk.annotations.defaults import defaults, update
from reactk.annotations.get_annotation_name import (
    get_annotation_name,
)
from reactk.annotations.get_metadata import (
    get_inner_type_value,
    get_metadata_of_type,
    get_props_type_from_callable,
)
from reactk.model.annotation_reader import AnnotationReader, read_annotations


MISSING = object()
type DiffMode = Literal["simple", "recursive", "never"]
if TYPE_CHECKING:
    from reactk.model.props.prop_value import PropValue


@dataclass(kw_only=True)
class Prop[T]:
    subsection: str | None = field(default=None)
    # FIXME: name behaves weirdly because it's inconsistent... should be fixed
    name: str = field(default="")
    no_value: Any | None = field(default=None)
    converter: Callable[[Any], Any] | None = field(default=None)
    value_type: type[T] | None = field(default=None)
    repr: Literal["simple", "recursive", "none"] = field(default="recursive")

    @property
    def has_default(self) -> bool:
        return self.no_value is not None

    def is_valid(self, input: Any):
        try:
            if input is None:
                return True
            if self.value_type is not None:
                if self.value_type is float:
                    return isinstance(input, int) or isinstance(input, float)
                x = check_type(input, self.value_type)
                return x is input
            return True
        except TypeCheckError as e:
            raise ValueError(f"Typecheck failed in {self.name}: {e.args[0]}") from e

    def assert_valid_value(self, value: Any):
        if not self.is_valid(value):
            raise ValueError(f"Invalid value {value} for {self}")

    def update(self, source_prop: "Prop") -> "Prop":
        return update(
            self, source_prop, "parent", "name", "no_value", "converter", "value_type"
        )

    def transform(self, key: str, value: Any) -> tuple[str, Any]:
        return (self.name or key, self.converter(value) if self.converter else value)

    def merge(self, other: "Prop") -> "Prop":
        return self.update(**{k: v for k, v in other.__dict__.items() if v is not None})

    def compute(self, key: str) -> tuple[str, Any] | None:
        return self.name if self.name else key, self.no_value

    def defaults(self, source_prop: "Prop") -> "Prop":
        return defaults(
            self, source_prop, "parent", "name", "no_value", "converter", "value_type"
        )

    def merge_setter(self, prop_setter: Callable) -> "Prop":
        first_arg = read_annotations(prop_setter).arg(1)
        prop_meta = self.defaults(
            Prop(value_type=first_arg.inner_type, name=prop_setter.__name__)
        )
        return prop_meta

    @overload
    def __call__[**P, R](
        self, f: Callable[Concatenate[R, P], Any]
    ) -> Callable[Concatenate[R, P], R]: ...

    @overload
    def __call__[**P, R](
        self,
    ) -> Callable[
        [Callable[Concatenate[R, P], Any]], Callable[Concatenate[R, P], R]
    ]: ...

    def __call__[**P, R](self, f: Any | None = None) -> Any:

        def apply(f):
            merged_prop = self.merge_setter(f)

            def set_prop(self, arg: Any):
                return self._copy(**{merged_prop.name: arg})

            AnnotationReader(set_prop).custom = merged_prop

            return set_prop

        return apply(f) if f else apply


def prop_setter[**P, R](
    f: Callable[Concatenate[R, P], Any],
) -> Callable[Concatenate[R, P], R]:

    def apply(f):
        merged_prop = self.merge_setter(f)

        def set_prop(self, arg: Any):
            return self._copy(**{merged_prop.name: arg})

        AnnotationReader(set_prop).custom = merged_prop

        return set_prop

    return apply(f)
