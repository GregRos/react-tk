from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Annotated, Any, Required, TypedDict, is_typeddict
from reactk.model2.ants.reflector import Reflector
from reactk.model2.util.core_reflection import get_attrs_downto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from reactk.model.trace.render_trace import RenderTrace
from reactk.model2.ants.readers import (
    Reader_Annotation,
    Reader_Class,
    Reader_Method,
)
from reactk.model2.ants.key_accessor import KeyAccessor
from reactk.model2.prop_ants.prop_meta import prop_meta, schema_meta, some_meta
from reactk.model2.prop_model.common import IS_REQUIRED
from reactk.model2.prop_model.prop import SomeProp
import funcy

from reactk.model2.prop_model.v_mapping import VMappingBase
from reactk.model2.ants.reflector import Reflector

from reactk.model2.prop_model.prop import Prop, PropSection


reflector = Reflector(inspect_up_to=(Mapping, TypedDict, "ShadowNode", object))


class MetaAccessor(KeyAccessor[some_meta]):
    @property
    def key(self) -> str:
        return "__reactk_meta__"


def _create_prop(
    path: tuple[str, ...], name: str, annotation: Reader_Annotation, meta: prop_meta
):
    from reactk.model2.prop_model.prop import Prop

    x: Any = annotation.inner_type
    return Prop[x](
        name=name,
        repr=meta.repr,
        no_value=meta.no_value,
        converter=meta.converter,
        computed_name=meta.name,
        subsection=meta.subsection,
        metadata=meta.metadata,
        value_type=x,
        path=(
            *path,
            name,
        ),
    )


def _create_schema(
    path: tuple[str, ...], name: str, annotation: Reader_Annotation, meta: schema_meta
):
    from reactk.model2.prop_model.prop import PropSection

    return PropSection(
        path=path,
        name=name,
        computed_name=meta.name,
        props=_read_props_from_class(path + (name,), annotation.inner_type),
        repr=meta.repr,
        metadata=meta.metadata,
    )


def _create(
    path: tuple[str, ...], name: str, annotation: Reader_Annotation, meta: some_meta
) -> SomeProp:
    match meta:
        case prop_meta() as p_m:
            return _create_prop(path, name, annotation, p_m)
        case schema_meta() as s_m:
            return _create_schema(path, name, annotation, s_m)
        case _:
            raise TypeError(f"Unknown meta type {type(meta)} for key {name}")


def _get_default_meta_for_prop(
    annotation: Reader_Annotation,
) -> some_meta:
    match annotation.target:
        case _ if issubclass(
            annotation.target, (Mapping, VMappingBase)
        ) or is_typeddict(annotation.target):
            return schema_meta(repr="recursive")
        case _:
            return prop_meta(
                no_value=IS_REQUIRED, converter=None, repr="recursive", metadata={}
            )


def _attrs_to_props(
    path: tuple[str, ...], meta: Mapping[str, Reader_Annotation]
) -> "Iterable[SomeProp]":
    for k, v in meta.items():
        if k.startswith("_"):
            continue
        metas = map(lambda x: x.target, v.metadata_of_type(schema_meta, prop_meta))
        fst = next(iter(metas), None)
        yield _create(path, k, v, fst or _get_default_meta_for_prop(v))


def _method_to_prop(path: tuple[str, ...], method: Reader_Method) -> "SomeProp":
    annotation = method.arg(1)
    meta = method.access(MetaAccessor).get() or _get_default_meta_for_prop(annotation)
    return _create(path, method.name, annotation, meta)


def _methods_to_props(path: tuple[str, ...], cls: type):
    methods = get_attrs_downto(cls, stop_at={object, Mapping})
    for k, v in methods.items():
        if not callable(v):
            continue
        if k.startswith("_"):
            continue
        p = _method_to_prop(path, reflector.method(v))
        if k == "__init__":
            if not isinstance(p, schema_meta):
                raise TypeError(
                    f"__init__ method must be annotated with schema_meta, got {type(p)}"
                )
        yield p


def _read_props_from_class(path: tuple[str, ...], cls: type):
    if not reflector.is_supported(cls):
        return ()
    reader = reflector.type(cls)

    normal_props = _attrs_to_props(path, reader.annotations)
    method_props = _methods_to_props(path, cls)
    all_props = (
        *normal_props,
        *method_props,
    )
    return all_props


def read_props_from_top_class(cls: type) -> "PropSection":
    props = [*_read_props_from_class((), cls)]
    init_block = funcy.first(x for x in props if x.name == "__init__")
    repr = "recursive"
    metadata = {}
    if init_block:
        props.remove(init_block)
        repr = init_block.repr
        metadata = init_block.metadata
    name = cls.__name__
    return PropSection(path=(), name=name, props=props, repr=repr, metadata=metadata)
