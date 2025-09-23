from abc import ABC, abstractmethod
from calendar import c
from logging import getLogger
from time import sleep
from tkinter import Label, Tk, Widget as TkWidget
from typing import Any, ClassVar, Self, final, override
from reactk.model2.prop_model import Prop_Schema, Prop_Mapping
from reactk.model2.prop_model import Prop_ComputedMapping
from reactk.rendering.future_actions import Create, Place, Replace, Unplace, Update
from reactk.tk.font import to_tk_font
from reactk.tk.make_clickthrough import make_clickthrough
from reactk.model.resource import Compat, Resource
from reactk.tk.widget import Widget

logger = getLogger(__name__)


class WidgetWrapperBase(Resource[Widget], ABC):
    resource: TkWidget

    @abstractmethod
    def migrate(self, node: Widget) -> Self: ...

    @abstractmethod
    @classmethod
    def create(cls, container: Resource, node: Widget) -> "WidgetWrapperBase": ...

    @override
    def get_compatibility(self, other: Widget) -> Compat:
        if self.node.type_name != other.type_name:
            return "recreate"
        elif self.node.__PROP_VALUES__.diff(other.__PROP_VALUES__):
            return "replace"
        else:
            return "update"

    def __init__(self, node: Widget, resource: TkWidget) -> None:
        super().__init__(node)
        self.resource = resource

    @staticmethod
    def _wrap(node: Widget, resource: TkWidget) -> "LabelWrapper":
        return LabelWrapper(node, resource)

    @override
    def is_same_resource(self, other: "WidgetWrapperBase.ThisResource") -> bool:
        return self.resource == other.resource

    @override
    def destroy(self) -> None:
        self.resource.destroy()

    @override
    def update(self, a: Prop_ComputedMapping, /) -> None:
        diff = a.values
        configure = diff.get("configure", {})
        if "font" in diff:
            configure["font"] = to_tk_font(diff["font"])
        if not configure:
            return
        self.resource.configure(**diff.get("configure", {}))

    @override
    def place(self, container: Resource, a: Prop_ComputedMapping, at: int, /) -> None:
        if not isinstance(container.resource, (TkWidget, Tk)):
            raise TypeError(f"Container {container} is not a TkWidget")
        logger.debug(f"Calling place for {self.node}")
        d = a.values
        pack = d.get("Pack", {})
        if not pack:  # pragma: no cover
            return
        slaves = container.resource.slaves()
        if slaves:
            if at >= len(slaves):
                pack["after"] = slaves[-1]
            elif at <= 0:
                pack["before"] = slaves[0]
            else:
                pack["after"] = slaves[at - 1]
        self.resource.pack_configure(**d.get("Pack", {}), in_=container.resource)
        logger.debug(f"Ending place for {self.node}")

    @override
    def unplace(self) -> None:
        self.resource.pack_forget()

    @override
    def replace(
        self, other: "WidgetWrapperBase.ThisResource", a: Prop_ComputedMapping, /
    ) -> None:
        self.resource.pack(after=self.resource, **a.values.get("Pack", {}))
        self.resource.pack_forget()


class LabelWrapper(WidgetWrapperBase):
    resource: TkWidget

    @classmethod
    def create(cls, container: "Resource", node: Widget) -> "LabelWrapper":
        lbl = Label(container.resource, name=node.to_string_marker("safe"))
        make_clickthrough(lbl)
        return __class__(node, lbl)

    def migrate(self, node: Widget) -> Self:

        x = LabelWrapper(node, self.resource)
        return x  # type: ignore
