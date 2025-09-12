from reactk.annotations.defaults import defaults, is_empty, update
from reactk.annotations.get_metadata import (
    get_inner_type_value,
    get_metadata_of_type,
    get_props_type_from_callable,
)
from reactk.model2.ants.get_methods import get_attrs_downto
from reactk.model.props.prop_dict import PropDict

from reactk.model.annotation_reader import AnnotationReader, CustomReader
from reactk.model.props.prop import Prop


from collections.abc import Mapping
from copy import copy
from dataclasses import dataclass, field
from inspect import isfunction
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Concatenate,
    Iterator,
    get_origin,
    get_type_hints,
    overload,
)

if TYPE_CHECKING:
    from reactk.model.props.prop_values import PValues

type SomeProp = Prop | PropSection


@dataclass
class PropSection(Mapping[str, SomeProp]):
    props: PropDict = field(default_factory=PropDict, init=False)
    recurse: bool = field(default=True)
    name: str = field(default="")

    def __iter__(self) -> Iterator[str]:
        return iter(self.props)

    def with_values(self, values: Mapping[str, Any]) -> "PValues":
        from reactk.model.props.prop_values import PValues

        return PValues(self, values)

    def defaults(self, base: "PropSection") -> "PropSection":
        return defaults(self, base, "recurse", "name")

    def update(self, base: "PropSection") -> "PropSection":
        return update(self, base, "recurse", "name")

    def __getitem__(self, key: str) -> SomeProp:
        return self.props[key]

    def __len__(self) -> int:
        return len(self.props)

    def merge_props(
        self, other: "Mapping[str, SomeProp] | PropSection"
    ) -> "PropSection":
        merged_props = self.props & (
            other.props if isinstance(other, PropSection) else other
        )
        clone = copy(self)
        clone.props = merged_props
        return clone

    __match_args__ = ("recurse",)

    def assert_valid_value(self, other: Mapping[str, Any]) -> None:
        assert isinstance(other, Mapping), f"Value {other} is not a mapping"
        for k, v in other.items():
            section = self.props
            value = section.get(k, None)
            if is_empty(value):
                raise ValueError(f"Key {k} doesn't exist in section {section}")
            value.assert_valid_value(v if v is not None else value.no_value)  # type: ignore

    @staticmethod
    def get_section_meta(f: Callable) -> "PropSection | None":
        return f.__annotations__["section"]

    def merge_setter(self, section_setter: Callable) -> "PropSection":
        section_props_type = get_props_type_from_callable(section_setter)
        section_meta = self.defaults(PropSection(name=section_setter.__name__))
        props = PropDict.from_type(section_props_type)

        return section_meta.merge_props(props)

    def merge_class(self, obj: type):
        props = PropDict()
        attrs = get_attrs_downto(obj, stop_at={object, PropSection, PropDict, dict})
        for k, f in attrs.items():
            if not isfunction(f):
                continue
            reader = AnnotationReader(f)

            if section := reader.get_section():
                if k == "__init__":
                    props = props.merge(section.value.props)
                else:
                    props = props.merge({k: section})
            elif prop := reader.get_prop():
                props = props.merge({k: prop})

        props = props.merge(
            x for x in PropDict.from_type(obj).items() if x[0] not in props
        )
        return self.merge_props(props)

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
        def get_or_init_prop_values(self, f: Callable) -> "PValues":
            if not getattr(self, "_props", None):
                custom_section = AnnotationReader(f).custom
                if not isinstance(custom_section, PropSection):
                    raise ValueError("PropSection missing custom annotation")
                self._props = custom_section.with_values({})
            return self._props

        def apply(f: Callable) -> Any:
            sect = self.merge_setter(f)

            def set_section(self, **args: Any):
                if f.__name__ == "__init__":
                    self._props = get_or_init_prop_values(self, f).merge(args)
                    return
                return self._copy(**{f.__name__: args})

            CustomReader(set_section).custom = sect

            return set_section

        return apply(f) if f else apply


def section_setter[**P, R](
    f: Callable[Concatenate[R, P], None],
) -> Callable[Concatenate[R, P], R]:
    def get_or_init_prop_values(target: object, f: Callable) -> "PValues":
        if not getattr(target, "_props", None):
            annotations = AnnotationReader(target.__class__)
            ctor_annotation = annotations["__init__"].value  # type: PropSection
            setattr(target, "_props", ctor_annotation.with_values({}))
        return target._props  # type: ignore

    def apply(f: Callable) -> Any:

        def set_section(self, **args: Any):
            if f.__name__ == "__init__":
                self._props = get_or_init_prop_values(self, f).merge(args)
                return
            return self._copy(**{f.__name__: args})

        return set_section

    return apply(f) if f else apply
