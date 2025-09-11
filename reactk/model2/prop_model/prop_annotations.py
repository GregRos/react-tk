from typing import TYPE_CHECKING
from reactk.model.annotation_reader import read_annotations
from reactk.model2.annotations import ClassReader

if TYPE_CHECKING:
    from reactk.model2.prop_model.prop import Prop, PropBlock


def read_props_from_class(cls: type) -> "PropBlock":
    reader = ClassReader(cls)
    normal_props = [x.metadata_of_type() for x in reader.annotations.values()]

    if not props:
        raise ValueError(f"No props found in class {cls.__name__}")

    return PropBlock(name=cls.__name__, props=props)
