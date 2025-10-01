from dataclasses import dataclass, field
import os
import sys
from time import sleep


from react_tk import (
    Ctx,
    Window,
    Widget,
    Component,
    Window,
    Font,
    WindowRoot,
)
from react_tk.tk.nodes.frame import Frame
from react_tk.tk.nodes.label import Label


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


my_root = WindowRoot(WindowComponent(), text="Hello, World!")

sleep(2)
my_root(text="Hello again!")
