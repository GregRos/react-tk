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
    Unpack,
    override,
)
from reactk.model2.prop_model import Prop
from reactk.model.context import Ctx
from reactk.rendering.renderer import ComponentMount
from reactk.rendering.stateful_reconciler import StatefulReconciler
from reactk.model.component import Component
from reactk.model2.prop_model import PropSection
from reactk.model.props.prop_section import section_setter
from reactk.tk.font import Font
from reactk.tk.make_clickthrough import make_clickthrough
import tkinter as tk

from reactk.model.shadow_node import ShadowNode, ShadowProps


class WidgetProps(ShadowProps):
    text: Annotated[NotRequired[str], Prop(no_value=" ", subsection="configure")]
    font: Annotated[NotRequired[Font], PropSection(recurse=False, name="font")]
    borderwidth: Annotated[NotRequired[int], Prop(no_value=0, subsection="configure")]
    border: Annotated[NotRequired[int], Prop(no_value=0, subsection="configure")]
    background: Annotated[
        NotRequired[str], Prop(no_value="#000001", subsection="configure")
    ]
    foreground: Annotated[
        NotRequired[str], Prop(no_value="#ffffff", subsection="configure")
    ]
    justify: Annotated[
        NotRequired[str], Prop(no_value="center", subsection="configure")
    ]
    wraplength: Annotated[NotRequired[int], Prop(no_value=None, subsection="configure")]
    relief: Annotated[NotRequired[str], Prop(no_value="solid", subsection="configure")]


class PackProps(ShadowProps):
    ipadx: Annotated[NotRequired[int], Prop(no_value=0)]
    ipady: Annotated[NotRequired[int], Prop(no_value=0)]
    fill: Annotated[
        NotRequired[Literal["both", "x", "y", "none"]], Prop(no_value="none")
    ]
    side: Annotated[
        NotRequired[Literal["top", "bottom", "left", "right"]], Prop(no_value="top")
    ]
    expand: Annotated[NotRequired[bool], Prop(no_value=False)]
    anchor: Annotated[
        NotRequired[Literal["n", "s", "e", "w", "ne", "nw", "se", "sw"]],
        Prop(no_value="n"),
    ]


class Widget(ShadowNode):

    @section_setter
    def __init__(
        self, **props: Unpack[Annotated[WidgetProps, PropSection(recurse=True)]]
    ) -> Annotated[None, PropSection(recurse=True)]: ...

    @section_setter
    def Pack(
        self, **props: Unpack[Annotated[PackProps, PropSection(recurse=False)]]
    ) -> None: ...


class Label(Widget):

    pass
