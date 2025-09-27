from tkinter import Tk
from typing import Literal, Tuple, TypedDict

from reactk.model.renderable.node.shadow_node import NodeProps

type AnchorType = Literal["lt", "rt", "lb", "rb"]


class Geometry(TypedDict):
    anchor_point: AnchorType
    width: int
    height: int
    x: int
    y: int
