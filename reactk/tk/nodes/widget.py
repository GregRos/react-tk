from abc import abstractmethod
from copy import copy
from dataclasses import dataclass
from itertools import groupby
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    ClassVar,
    Generator,
    Literal,
    Never,
    NotRequired,
    Self,
    TypedDict,
    Unpack,
    override,
)

from expression import Some
from reactk.model.renderable.node.prop_value_accessor import PropValuesAccessor

from reactk.model.props.annotations import prop_meta, schema_meta, schema_setter
from reactk.rendering.actions.node_reconciler import ReconcilerBase
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


class PackProps(TypedDict):
    ipadx: Annotated[NotRequired[int], prop_meta(no_value=0)]
    ipady: Annotated[NotRequired[int], prop_meta(no_value=0)]
    fill: Annotated[
        NotRequired[Literal["both", "x", "y", "none"]], prop_meta(no_value="none")
    ]
    side: Annotated[
        NotRequired[Literal["top", "bottom", "left", "right"]],
        prop_meta(no_value="top"),
    ]
    expand: Annotated[NotRequired[bool], prop_meta(no_value=False)]
    anchor: Annotated[
        NotRequired[Literal["n", "s", "e", "w", "ne", "nw", "se", "sw"]],
        prop_meta(no_value="n"),
    ]


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
