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

from expression import Some


from reactk.model2.prop_ants import prop_meta, schema_meta, schema_setter, prop_setter
from reactk.model.component import Component
from reactk.model.shadow_node import (
    NodeProps,
    ShadowNode,
)
from reactk.rendering.reconciler import Reconciler
from reactk.tk.nodes.widget import Widget
from reactk.tk.reconcilers.widget_reconciler import WidgetReconciler
from reactk.tk.reconcilers.window_reconciler import WindowReconciler
from reactk.tk.types.geometry import Geometry
from reactk.rendering.reconciler import reconciler


class WindowProps(NodeProps):
    topmost: Annotated[
        NotRequired[bool], prop_meta(subsection="attributes", no_value=False)
    ]
    background: Annotated[
        NotRequired[str], prop_meta(subsection="configure", no_value=Some(None))
    ]
    transparent_color: Annotated[
        NotRequired[str],
        prop_meta(
            subsection="attributes", name="transparentcolor", no_value=Some(None)
        ),
    ]
    override_redirect: Annotated[NotRequired[bool], prop_meta(no_value=False)]
    alpha: Annotated[
        NotRequired[float], prop_meta(subsection="attributes", no_value=1.0)
    ]


@reconciler(WindowReconciler)
class Window(ShadowNode[Widget]):

    @schema_setter()
    def __init__(self, **props: Unpack[WindowProps]) -> None: ...

    @schema_setter()
    def Geometry(self, **props: Unpack[Geometry]) -> None: ...
