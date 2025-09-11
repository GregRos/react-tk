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
    NotRequired,
    Self,
    TypedDict,
    Unpack,
    override,
)
from reactk.model.context import Ctx
from reactk.model2.prop_model.c_meta import prop_meta, schema_meta, schema_setter
from reactk.model2.rendering_model.s_node import InitPropsBase, ShNode
from reactk.rendering.renderer import ComponentMount
from reactk.rendering.stateful_reconciler import StatefulReconciler
from reactk.model.component import Component
from reactk.tk.font import Font
import tkinter as tk


class WidgetProps(InitPropsBase):
    text: Annotated[NotRequired[str], prop_meta(no_value=" ", subsection="configure")]
    font: Annotated[NotRequired[Font], schema_meta(repr="simple", name="font")]
    borderwidth: Annotated[
        NotRequired[int], prop_meta(no_value=0, subsection="configure")
    ]
    border: Annotated[NotRequired[int], prop_meta(no_value=0, subsection="configure")]
    background: Annotated[
        NotRequired[str], prop_meta(no_value="#000001", subsection="configure")
    ]
    foreground: Annotated[
        NotRequired[str], prop_meta(no_value="#ffffff", subsection="configure")
    ]
    justify: Annotated[
        NotRequired[str], prop_meta(no_value="center", subsection="configure")
    ]
    wraplength: Annotated[
        NotRequired[int], prop_meta(no_value=None, subsection="configure")
    ]
    relief: Annotated[
        NotRequired[str], prop_meta(no_value="solid", subsection="configure")
    ]


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


class Widget(ShNode):

    @schema_setter()
    def __init__(self, **props: Unpack[WidgetProps,]) -> None: ...

    @schema_setter(repr="simple")
    def Pack(self, **props: Unpack[PackProps]) -> None: ...


class Label(Widget):

    pass
