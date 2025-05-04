from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Iterable, Iterator
from reactk.model.props.prop import Prop

if TYPE_CHECKING:
    from reactk.model.props.prop_section import PropSection

type SomeProp = Prop | PropSection


class PropDict(Mapping[str, SomeProp]):
    _props: Mapping[str, SomeProp]

    def __init__(
        self, props: Mapping[str, SomeProp] | Iterable[tuple[str, SomeProp]] = {}
    ):
        self._props = (
            dict(props) if isinstance(props, Mapping) else {k: v for k, v in props}
        )

    def get_prop(self, key: str) -> Prop:
        result = self[key]
        assert isinstance(result, Prop), f"Key {key} is not a PropDef"
        return result

    def get_section(self, key: str) -> "PropSection":
        result = self[key]
        assert isinstance(result, PropSection), f"Key {key} is not a section"
        return result

    def __and__(self, other: Mapping[str, SomeProp]) -> "PropDict":
        return self.merge(other)

    def __contains__(self, key: Any) -> bool:
        return key in self._props

    def merge(
        self, other: Mapping[str, SomeProp] | Iterable[tuple[str, SomeProp]]
    ) -> "PropDict":
        result = {}
        other = PropDict(other)
        for key in self.keys() | other.keys():
            if key not in self:
                result[key] = other[key]
                continue
            elif key not in other:
                result[key] = self[key]
                continue
            self_prop = self[key]
            other_prop = other[key]
            assert isinstance(self_prop, PropSection) and isinstance(
                other_prop, PropSection
            ), f"Key {key} exists in both dicts, but is not a section in at least one. Can't be merged."
            result[key] = self_prop.merge_props(other_prop)

        return PropDict(result)

    def set(self, **props: Prop) -> "PropDict":
        return self.merge(props)

    def __len__(self) -> int:
        return len(self._props)

    def __iter__(self) -> Iterator[str]:
        return iter(self._props)

    def __getitem__(self, key: str) -> SomeProp:
        return self._props[key]

    def assert_match(self, other: Mapping[str, Any]) -> None:
        errors = []
        for key in self.keys() | other.keys():
            if key not in self:
                errors += [f"Key of input map {key} doesn't exist in self."]
            if key not in other:
                errors += [f"Key of self map {key} doesn't exist in input."]
            if self[key] != other[key]:
                errors += [f"Key {key} doesn't match."]

        if errors:
            raise ValueError("\n".join(errors))
