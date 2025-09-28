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

from reactk.model.renderable.node.prop_value_accessor import PropValuesAccessor

from reactk.model.props.annotations import schema_meta, schema_setter
from reactk.rendering.actions.node_reconciler import ReconcilerBase
from reactk.tk.props.pack import PackProps
from reactk.tk.props.text import TextProps
from reactk.tk.props.width_height import WidthHeightProps
from reactk.tk.props.background import BackgroundProps
from reactk.tk.props.border import BorderProps
from reactk.tk.reconcilers.widget_reconciler import (
    FrameReconciler,
    LabelReconciler,
    WidgetReconciler,
)
from reactk.tk.types.font import Font
from reactk.model.renderable.node.shadow_node import NodeProps, ShadowNode
from reactk.rendering.actions.node_reconciler import reconciler


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
