from copy import copy
from dataclasses import dataclass
from tkinter import Tk
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


from reactk.model.resource import Compat
from reactk.model2.prop_ants import prop_meta, schema_meta, schema_setter, prop_setter
from reactk.model.component import Component
from reactk.model.shadow_node import (
    InitPropsBase,
    ShadowNode,
)
from reactk.rendering.reconciler import Reconciler
from reactk.tk.nodes.widget import Widget
from reactk.tk.types.geometry import Geometry


class WindowProps(InitPropsBase):
    topmost: Annotated[NotRequired[bool], prop_meta(subsection="attributes")]
    background: Annotated[NotRequired[str], prop_meta(subsection="configure")]
    transparent_color: Annotated[
        NotRequired[str], prop_meta(subsection="attributes", name="transparentcolor")
    ]
    override_redirect: Annotated[NotRequired[bool], prop_meta()]
    alpha: Annotated[NotRequired[float], prop_meta(subsection="attributes")]


class Window(ShadowNode[Widget]):

    @schema_setter()
    def __init__(self, **props: Unpack[WindowProps]) -> None: ...

    @schema_setter()
    def Geometry(self, **props: Unpack[Geometry]) -> None: ...

    @override
    def _get_compatibility(self, other: "Window.This") -> Compat:
        return "update"

    @classmethod
    def get_reconciler(cls) -> type[Reconciler[Any]]:
        from reactk.tk.reconcilers.window_reconciler import WindowReconciler

        return WindowReconciler
