from dataclasses import dataclass, field
import os
import sys
from time import sleep

from funcy import first


from react_tk import Ctx, Window, Widget, Component, Window, Font, WindowRoot, Button
from react_tk.tk.nodes.frame import Frame
from react_tk.tk.nodes.label import Label


@dataclass(kw_only=True)
class ExampleComponent_1(Component[Widget]):
    text: str

    def render(self):

        return [
            Label(
                key="em_1.label1",
                text=self.text,
                background="#000001",
                foreground="#ffffff",
                font=Font(family="Arial", size=20, style="bold"),
            ).Pack(ipadx=20, ipady=15, fill="both"),
            Label(
                key="em_1.label2",
                text="Another label",
                background="#000001",
            ),
            Label(
                key="em_1.label3",
                text="Yet another label",
                background="#000001",
            ),
        ]


@dataclass(kw_only=True)
class ExampleComponent_2(Component[Widget]):
    text: str

    def render(self):

        return Label(
            key="em_2.label1",
            text=self.text,
            background="#000001",
            foreground="#ffffff",
            font=Font(family="Arial", size=20, style="bold"),
        ).Pack(ipadx=20, ipady=15, fill="both")


@dataclass(kw_only=True)
class ChangingComponent(Component[Widget]):
    text: str

    def render(self):
        return Button(
            key="cm.button", text="press me", on_click=lambda: print("pressed")
        )
        if self.ctx.first_item:
            return Label(
                key="cm.label",
                text="First item",
            )
        return []


@dataclass(kw_only=True)
class WindowComponent(Component[Window]):

    def render(self):
        if self.ctx.component_id == 1:
            child = ExampleComponent_1(text=self.ctx.text)
        else:
            child = ExampleComponent_2(text=self.ctx.text)

        return Window(topmost=True, background="black", alpha=85).Geometry(
            width=500, height=500, x=500, y=500, anchor_point="lt"
        )[ChangingComponent(text="I'm changing"), child]


my_root = WindowRoot(
    WindowComponent(), text="component:1, first:True", component_id=1, first_item=True
)
ctx = my_root.ctx


@ctx.schedule(delay=4, always_run=True)
def step_1():
    my_root(text="component:2, first:False", component_id=2, first_item=False)


@ctx.schedule(delay=6, always_run=True)
def step_2():
    my_root(text="component:1, first:True", component_id=1, first_item=False)


@ctx.schedule(delay=8, always_run=True)
def step_3():
    my_root(first_item=True)
