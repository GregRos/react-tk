from abc import abstractmethod
from copy import copy
from dataclasses import dataclass
from itertools import groupby
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Generator,
    Never,
    Self,
    Unpack,
    override,
)

from react_tk.renderable.node.prop_value_accessor import PropValuesAccessor

from react_tk.props.annotations import schema_meta, schema_setter
from react_tk.rendering.actions.node_reconciler import ReconcilerBase
from react_tk.tk.props.pack import PackProps
from react_tk.tk.props.text import TextProps
from react_tk.tk.props.width_height import WidthHeightProps
from react_tk.tk.props.background import BackgroundProps
from react_tk.tk.props.border import BorderProps
from react_tk.tk.reconcilers.widget_reconciler import (
    FrameReconciler,
    LabelReconciler,
    WidgetReconciler,
)
from react_tk.tk.types.font import Font
from react_tk.renderable.node.shadow_node import NodeProps, ShadowNode
from react_tk.rendering.actions.node_reconciler import reconciler


class LabelProps(NodeProps, WidthHeightProps, BorderProps, BackgroundProps, TextProps):
    pass


class FrameProps(NodeProps, WidthHeightProps, BorderProps, BackgroundProps):
    pass


@reconciler(WidgetReconciler)
class Widget[Kids: ShadowNode[Any]](ShadowNode[Kids]):

    @schema_setter(repr="simple")
    def Pack(self, **props: Unpack[PackProps]) -> None: ...


@reconciler(LabelReconciler)
class Label(Widget[Never]):
    @schema_setter()
    def __init__(self, **props: Unpack[LabelProps]) -> None: ...


@reconciler(FrameReconciler)
class Frame(Widget[Widget[Any]]):
    @schema_setter()
    def __init__(self, **props: Unpack[FrameProps]) -> None: ...
