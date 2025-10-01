from dataclasses import dataclass
from typing import Self
from react_tk.renderable.component import AbsCtx, Component, RenderResult
from react_tk.renderable.context import Ctx
from react_tk.tk.nodes.label import Label
from react_tk.tk.nodes.widget import Widget
from react_tk.tk.nodes.window import Window
from react_tk.tk.types.font import Font


@dataclass(kw_only=True)
class StuffComponent(Component[Widget]):
    text: str

    def render(self):
        return Label(
            text=self.text,
            background="#000001",
            foreground="#ffffff",
            font=Font(family="Arial", size=20, style="bold"),
        ).Pack(ipadx=20, ipady=15, fill="both")


@dataclass(kw_only=True)
class WindowComponent(Component[Window]):

    def render(self):
        x = StuffComponent(text=self.ctx.text)
        return Window(topmost=True, background="black", alpha=85).Geometry(
            width=500, height=500, x=500, y=500, anchor_point="lt"
        )[x]
