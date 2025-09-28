from abc import ABC, abstractmethod
from collections.abc import Mapping
from copy import copy
from dataclasses import dataclass, is_dataclass
from inspect import isabstract
from pyclbr import Class
import sys
from typing import (
    TYPE_CHECKING,
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
    Unpack,
)

from expression import Some
from reactk.model.renderable.node.prop_value_accessor import (
    PropValuesAccessor,
    PropsAccessor,
)
from reactk.model.renderable.renderable_base import RenderableBase
from reactk.model.renderable.trace import (
    ConstructTraceAccessor,
    RenderTrace,
    RenderTraceAccessor,
)
from reactk.model.props.annotations.prop_meta import prop_meta
from reactk.model.props.annotations.decorators import HasChildren, prop_getter
from reactk.model.props.annotations.create_props import (
    read_props_from_top_class,
)
from reactk.model.props.impl.common import KeyedValues
from reactk.model.props.impl.prop import Prop_Mapping

if TYPE_CHECKING:
    from reactk.rendering.actions.reconciler import ReconcilerBase


class HasPropsSchema:

    def __init_subclass__(cls) -> None:
        if isabstract(cls):
            return

        props_block = read_props_from_top_class(cls)
        PropsAccessor(cls).set(props_block)

    def __merge__(self, input_values: KeyedValues = {}, **kwargs: Any) -> Self:
        input_values = {
            **input_values,
            **kwargs,
        }
        schema = PropsAccessor(self).get()
        values = PropValuesAccessor(self)
        if not values:
            pbv = Prop_Mapping(prop=schema, value=input_values, old=None)
            values = pbv
        else:
            values = values.get().update(input_values)
        clone = copy(self)
        PropValuesAccessor(clone).set(values)
        return clone


class NodeProps(TypedDict):
    key: Annotated[NotRequired[str], prop_meta(no_value=Some(None))]
    KIDS: Annotated[NotRequired[Iterable[Any]], prop_meta(no_value=())]


class ShadowNode[Kids: ShadowNode[Any] = Never](
    RenderableBase, HasPropsSchema, HasChildren[Kids], ABC
):

    @property
    def PROPS(self) -> Prop_Mapping:
        return PropValuesAccessor(self).get()

    @prop_getter()
    def KIDS(self) -> Iterable["ShadowNode[Any]"]: ...

    @prop_getter()
    def key(self) -> str: ...

    @property
    def __uid__(self):
        return RenderTraceAccessor(self).get().to_string("id")
