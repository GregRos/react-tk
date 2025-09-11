from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Iterable, Iterator
from reactk.model.annotation_reader import AnnotationReader
from reactk.model.props.prop import Prop

if TYPE_CHECKING:
    from reactk.model.props.prop_section import PropSection

type SomeProp = Prop | PropSection


class PropDict(Mapping[str, SomeProp]):
    _props: Mapping[str, SomeProp]

    def __init__(
        self, props: Mapping[str, SomeProp] | Iterable[tuple[str, SomeProp]] = {}
    ):
        x = (
            dict[str, SomeProp](props)
            if isinstance(props, Mapping)
            else {k: v for k, v in props}
        )
        self._props = x

    @staticmethod
    def from_type(x: type) -> "PropDict":
        from reactk.model.props.prop_section import PropSection

        def _items():
            for k, v in AnnotationReader(x).items():
                prop_meta = v.metadata.of_types(PropSection, Prop)
                match prop_meta:
                    case Prop():
                        yield k, prop_meta.defaults(
                            Prop(value_type=v.inner_type, name=k)
                        )
                    case PropSection():
                        yield k, prop_meta.defaults(PropSection(name=k)).merge_class(
                            v.inner_type or type(object)
                        )

                if k.startswith("_"):
                    continue
                if prop := v.metadata.of_types(Prop):
                    yield k, prop.defaults(Prop(value_type=v.inner_type, name=k))
                elif section := v.metadata.of_types(PropSection):
                    yield k, section.defaults(PropSection(name=k)).merge_class(
                        v.inner_type or type(object)
                    )
                elif v.inner_type and issubclass(v.inner_type, Mapping):
                    yield k, PropSection(name=k).merge_class(
                        v.inner_type or type(object)
                    )
                else:
                    yield k, Prop(value_type=v.inner_type, name=k)

        return PropDict(dict(_items()))

    def __contains__(self, key: Any) -> bool:
        return key in self._props

    def __len__(self) -> int:
        return len(self._props)

    def __iter__(self) -> Iterator[str]:
        return iter(self._props)

    def __getitem__(self, key: str) -> SomeProp:
        return self._props[key]
