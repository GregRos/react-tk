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


from reactk.model.props.prop_section import PropSection, section_setter
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
        self, child: Annotated[Widget | Component[Widget], Prop(repr="simple")]
    ): ...

    @section_setter
    def __init__(
        self, **props: Unpack[Annotated[WindowProps, PropSection(recurse=True)]]
    ): ...

    @section_setter
    def Geometry(
        self, **props: Unpack[Annotated[Geometry, PropSection(recurse=True)]]
    ): ...
