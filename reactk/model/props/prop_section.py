from reactk.annotations.defaults import defaults, is_empty, update
from reactk.annotations.get_metadata import (
    get_inner_type_value,
    get_metadata_of_type,
    get_props_type_from_callable,
)
from reactk.annotations.get_methods import get_attrs_downto
from reactk.model.props.prop_dict import PropDict

from reactk.model.annotation_reader import AnnotationReader
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


def get_props(section_type: type):

    type_metadata = get_type_hints(
        section_type, include_extras=True, localns={"Node": "object"}
    )
    for k, v in type_metadata.items():
        inner_type = get_inner_type_value(v) or v
        prop = get_metadata_of_type(v, Prop, PropSection)
        match prop:
            case None if (x := get_origin(inner_type)) and issubclass(x, Mapping):
                yield k, PropSection(name=k).merge_class(inner_type)
            case None:
                yield k, Prop(value_type=inner_type, name=k)
            case Prop():
                yield k, prop.defaults(Prop(value_type=inner_type, name=k))
            case PropSection():
                yield k, prop.defaults(PropSection(name=k)).merge_class(inner_type)


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

    def transform(self, key: str, value: Any) -> tuple[str, Any]:
        from reactk.model.props.prop_values import PValues

        assert isinstance(value, Mapping), f"Value {value} is not a mapping"
        return key, PValues(self, value)

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
        props = PropDict()
        all_props = get_props(section_props_type)
        for k, v in all_props:
            props = props.merge({k: v})
        return section_meta.merge_props(props)

    def merge_class(self, obj: type):
        props = PropDict()
        attrs = get_attrs_downto(obj, stop_class=object)
        for k, f in attrs.items():
            if not isfunction(f):
                continue
            match AnnotationReader(f).metadata:
                case None:
                    continue
                case PropSection() as section:
                    if k == "__init__":
                        props = props.merge(section.props)
                    else:
                        props = props.merge({k: section})
                case Prop() as prop:
                    props = props.merge({k: prop})
        props = props.merge(x for x in get_props(obj) if x[0] not in props)
        return self.merge_props(props)

    @overload
    def __call__[
        **P, R
    ](self, f: Callable[Concatenate[R, P], None]) -> Callable[Concatenate[R, P], R]: ...

    @overload
    def __call__[
        **P, R
    ](self) -> Callable[
        [Callable[Concatenate[R, P], Any]], Callable[Concatenate[R, P], R]
    ]: ...

    def __call__[**P, R](self, f: Any | None = None) -> Any:
        def get_or_init_prop_values(self):
            if not getattr(self, "_props", None):
                self._props = AnnotationReader(self.__class__).section.with_values({})
            return self._props

        def apply(f):
            sect = self.merge_setter(f)

            def set_section(self, **args: Any):
                if f.__name__ == "__init__":
                    self._props = get_or_init_prop_values(self).merge(args)
                    return
                return self._copy(**{f.__name__: args})

            AnnotationReader(set_section).section = sect

            return set_section

        return apply(f) if f else apply
