from typing import NotRequired, Annotated, Unpack

from reactk.model2.examples.widget_ex import Widget
from reactk.model2.prop_model.c_meta import HasChildren, prop_meta, schema_setter
from reactk.model2.rendering_model.component import Comp
from reactk.model2.rendering_model.s_node import InitPropsBase, ShNode


class WindowPropsEx(InitPropsBase):
    topmost: Annotated[NotRequired[bool], prop_meta(subsection="attributes")]
    background: Annotated[NotRequired[str], prop_meta(subsection="configure")]
    transparent_color: Annotated[
        NotRequired[str],
        prop_meta(subsection="attributes", name="transparentcolor"),
    ]
    override_redirect: Annotated[
        NotRequired[bool], prop_meta(name="overrideredirect", subsection="attributes")
    ]
    alpha: Annotated[NotRequired[float], prop_meta(subsection="attributes")]


class WindowEx(ShNode[Widget]):  # type: ignore

    @schema_setter()
    def __init__(self, **props: Unpack[WindowPropsEx]): ...

    # @section_setter
    # def Geometry(
    #     self, **props: Unpack[Geometry]
    # ): ...


WindowEx()[Widget(text="Hello, World!", background="#ff0000", foreground="#ffffff")]
