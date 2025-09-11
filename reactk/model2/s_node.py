from copy import copy
from typing import Any, ClassVar, Self
from reactk.model2.prop_model.prop_annotations import read_props_from_class
from reactk.model2.prop_model.prop import PropBlock, PropBlockValues


class ShNode:
    _props: PropBlockValues
    PROPS: ClassVar[PropBlock]

    def __init_subclass__(cls) -> None:
        cls._embed_props_block()

    @classmethod
    def _embed_props_block(cls) -> None:
        props_block = read_props_from_class(cls)
        cls.PROPS = props_block

    def _copy(self, **overrides: Any) -> Self:
        clone = copy(self)
        # FIXME: This is a hack that shouldn't exist.
        # trace and key should not be props at all
        clone._props = self._props.update(overrides)

        return clone
