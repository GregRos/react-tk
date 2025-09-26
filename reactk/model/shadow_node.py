from abc import ABC, abstractmethod
from collections.abc import Mapping
from copy import copy
from dataclasses import dataclass, is_dataclass
from inspect import isabstract
from typing import (
    Annotated,
    Any,
    ClassVar,
    Iterable,
    Never,
    NotRequired,
    Protocol,
    Required,
    Self,
    TypedDict,
)
from reactk.model.component import Component
from reactk.model.resource import Compat
from reactk.model.trace.key_tools import Display
from reactk.model.trace.render_trace import RenderTrace
from reactk.model2.prop_ants.prop_meta import prop_meta
from reactk.model2.prop_ants.decorators import HasChildren, prop_getter
from reactk.model2.prop_ants.create_props import (
    read_props_from_top_class,
)
from reactk.model2.prop_model.common import KeyedValues
from reactk.model2.prop_model.prop import Prop_Schema, Prop_Mapping
from reactk.model2.util.dict import deep_merge
from reactk.tk.nodes.widget import Widget


class _WithDefaults(TypedDict):
    __TRACE__: Annotated[Required[RenderTrace], prop_meta(repr="simple")]
    __CHILDREN__: Annotated[NotRequired[Iterable[Any]], prop_meta(no_value=())]


class HasPropsSchema:
    __PROPS__: ClassVar[Prop_Schema]
    __PROP_VALUES__: Prop_Mapping

    def __init_subclass__(cls) -> None:
        if isabstract(cls):
            return

        props_block = read_props_from_top_class(cls)
        has_trace = read_props_from_top_class(_WithDefaults)
        props_block = props_block.update(has_trace)
        cls.__PROPS__ = props_block

    def __merge__(self, other: KeyedValues = {}, **kwargs: Any) -> Self:
        values = self.__PROP_VALUES__
        schema = self.__PROPS__
        if not values:
            pbv = Prop_Mapping(prop=schema, value={}, old=None)
            self.__PROP_VALUES__ = pbv
        new_pbv = values.update(other).update(kwargs)
        clone = copy(self)
        clone.__PROP_VALUES__ = new_pbv
        return clone


class InitPropsBase(TypedDict):
    key: Annotated[NotRequired[str], prop_meta(no_value=None)]


@dataclass
class ShadowNode[Kids: ShadowNode = Never](
    HasPropsSchema, HasChildren[Kids | Component[Kids]], ABC
):
    type This = ShadowNode[Kids]

    @prop_getter()
    def __CHILDREN__(self) -> Iterable[Kids | Component[Kids]]: ...

    @prop_getter()
    def __TRACE__(self) -> RenderTrace: ...

    def to_string_marker(self, display: Display) -> str:
        return self.__TRACE__.to_string(display)

    @abstractmethod
    def get_compatibility(self, other: This) -> Compat: ...

    @property
    def type_name(self) -> str:
        return self.__class__.__name__

    @prop_getter()
    def key(self) -> str: ...

    @property
    def uid(self):
        return self.__TRACE__.to_string("id")
