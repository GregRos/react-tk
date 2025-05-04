from copy import copy
from dataclasses import dataclass
from typing import (
    Annotated,
    Any,
    Literal,
    NotRequired,
    Self,
    Tuple,
    Unpack,
    override,
)


from reactk.model.props.prop_section import PropSection
from reactk.model.props.prop import Prop
from reactk.model.component import Component
from reactk.model.shadow_node import (
    InitPropsBase,
    ShadowNode,
    ShadowProps,
)
from reactk.tk.widget import Widget
from reactk.tk.geometry import Geometry


class WindowProps(ShadowProps):
    topmost: Annotated[NotRequired[bool], Prop(subsection="attributes")]
    background: Annotated[NotRequired[str], Prop(subsection="configure")]
    transparent_color: Annotated[
        NotRequired[str], Prop(subsection="attributes", name="transparentcolor")
    ]
    override_redirect: Annotated[NotRequired[bool], Prop()]
    alpha: Annotated[NotRequired[float], Prop(subsection="attributes")]


class Window(ShadowNode, Component[Widget]):  # type: ignore

    @Prop(repr="simple")
    def child(
        self,
        child: Widget | Component[Widget],
    ): ...

    @PropSection(recurse=True)
    def __init__(self, **props: Unpack[WindowProps]): ...

    @PropSection(recurse=False)
    def Geometry(self, **props: Unpack[Geometry]): ...
