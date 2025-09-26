from dataclasses import dataclass, field
import os
import sys
from time import sleep


from reactk import Ctx, Window, Label, Widget, Component
from reactk.tk.types.font import Font


@dataclass(kw_only=True)
class StuffComponent(Component[Widget]):
    text: str

    def render(self, yld, _):
        yld(
            Label(
                text=self.text,
                background="#000001",
                foreground="#ffffff",
                font=Font(family="Arial", size=20, style="bold"),
            ).Pack(ipadx=20, ipady=15, fill="both")
        )


@dataclass(kw_only=True)
class WindowComponent(Component[Window]):
    def render(self, yld, ctx: Ctx):
        yld(
            Window(topmost=True, background="black", alpha=85).Geometry(
                width=500, height=500, x=500, y=500, anchor_point="lt"
            )[StuffComponent(text=ctx.text)]
        )


MyTK = WindowMount(WindowComponent())

MyTK(text="Hello, World!")
sleep(2)
MyTK(text="Hello again!")
