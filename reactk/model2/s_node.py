from abc import ABC
from collections.abc import Mapping
from copy import copy
from dataclasses import is_dataclass
from inspect import isabstract
from typing import Annotated, Any, ClassVar, Protocol, Required, Self, TypedDict
from reactk.model.trace.render_trace import RenderTrace
from reactk.model2.key_accessor import KeyAccessor
from reactk.model2.prop_model.c_meta import prop_meta
from reactk.model2.prop_model.prop_annotations import (
    read_props_from_top_class,
)
from reactk.model2.prop_model.prop import PropBlock, PropBlockValues
from reactk.model2.v_mapping import deep_merge


class _WithTrace(TypedDict):
    __TRACE__: Annotated[Required[RenderTrace], prop_meta(repr="simple")]


class HasPropsSchema:
    __PROPS__: ClassVar[PropBlock]
    __PROP_VALUES__: PropBlockValues

    def __init_subclass__(cls) -> None:
        if isabstract(cls):
            return
        if not is_dataclass(cls):
            raise TypeError(f"Class {cls.__name__} must be a dataclass to use props")
        props_block = read_props_from_top_class(cls)
        has_trace = read_props_from_top_class(_WithTrace)
        props_block = props_block.update(has_trace)
        cls.__PROPS__ = props_block

    def __merge__(self, other: Mapping[str, Any]) -> Self:
        values = self.__PROP_VALUES__
        schema = self.__PROPS__
        if not values:
            pbv = PropBlockValues(schema=schema, values={}, old=None)
            self.__PROP_VALUES__ = pbv
        new_pbv = values.update(other)
        clone = copy(self)
        clone.__PROP_VALUES__ = new_pbv
        return clone


class ShNode(HasPropsSchema, ABC):
    pass


class A(ShNode):
    pass
