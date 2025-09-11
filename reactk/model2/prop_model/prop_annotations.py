from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING
from reactk.model.annotation_reader import read_annotations
from reactk.model2.annotations import AnnotationWrapper2, ClassReader
from reactk.model2.prop_model.c_meta import prop_meta, schema_meta, some_meta
from reactk.model2.prop_model.prop import SomeProp

if TYPE_CHECKING:
    from reactk.model2.prop_model.prop import Prop, PropBlock


def meta_to_props(
    path: tuple[str, ...], meta: Mapping[str, AnnotationWrapper2]
) -> "Iterable[SomeProp]":
    for k, v in meta.items():
        meta_thing = v.metadata_of_type(schema_meta, prop_meta)
        match meta_thing:
            case prop_meta(
                repr=repr, no_value=no_value, converter=converter, metadata=meta
            ):
                yield Prop(
                    name=k,
                    repr=repr,
                    no_value=no_value,
                    converter=converter,
                    metadata=meta,
                    value_type=v.inner_type,
                    path=path + (k,),
                )
            case schema_meta(repr=repr, metadata=meta):
                yield PropBlock(
                    name=k,
                    props=_read_props_from_class(path + (k,), v.inner_type),
                    repr=repr,
                    metadata=meta,
                )
            case _:
                raise TypeError(f"Unknown meta type {type(v)} for key {k}")


def _read_props_from_class(path: tuple[str, ...], cls: type):
    reader = ClassReader(cls)

    normal_props = {k: x for k, x in reader.annotations.items()}
    method_props = {k: x.get_arg(1) for k, x in reader.methods.items()}
    all_props = {**normal_props, **method_props}

    return meta_to_props(path, all_props)


def read_props_from_top_class(cls: type) -> "PropBlock":
    props = _read_props_from_class((), cls)
    name = cls.__name__
    return PropBlock(name=name, props=props, repr="recursive", metadata={})
