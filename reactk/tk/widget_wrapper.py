from logging import getLogger
from time import sleep
from tkinter import Label, Tk, Widget as TkWidget
from typing import Any, ClassVar, Self, final, override
from reactk.model2.prop_model import PropSection, PValues
from reactk.tk.font import to_tk_font
from reactk.tk.make_clickthrough import make_clickthrough
from reactk.model.resource import Compat, Resource
from reactk.tk.widget import Widget

logger = getLogger(__name__)


class WidgetWrapper(Resource[Widget]):

    @staticmethod
    @override
    def node_type() -> type[Widget]:
        return Widget

    @final
    @override
    def migrate(self, node: Widget) -> Self:

        x = WidgetWrapper(node, self.resource)
        return x  # type: ignore

    @staticmethod
    def create(tk: Tk, node: Widget) -> "WidgetWrapper":

        match node.type_name:
            case "Label":
                lbl = Label(tk, name=node.to_string_marker("safe"))
                make_clickthrough(lbl)
                return __class__(node, lbl)

            case _:
                raise ValueError(f"Unknown type: {node.type_name}")

    @override
    def get_compatibility(self, other: Widget) -> Compat:
        if self.node.type_name != other.type_name:
            return "recreate"
        elif self.node._props["Pack"] != other._props["Pack"]:
            return "replace"
        else:
            return "update"

    def __init__(self, node: Widget, resource: TkWidget) -> None:
        super().__init__(node)
        self.resource = resource

    @staticmethod
    def _wrap(node: Widget, resource: TkWidget) -> "WidgetWrapper":
        return WidgetWrapper(node, resource)

    @override
    def is_same_resource(self, other: Self) -> bool:
        return self.resource == other.resource

    @override
    def destroy(self) -> None:
        self.resource.destroy()

    @override
    def update(self, props: PValues) -> None:

        _, diff = props.compute()
        configure = diff.get("configure", {})
        if "font" in diff:
            configure["font"] = to_tk_font(diff["font"])
        if not configure:
            return
        self.resource.configure(**diff.get("configure", {}))
        x = 1

    @override
    def place(self) -> None:
        logger.debug(f"Calling place for {self.node}")
        _, d = self.node._props.compute()
        pack = d.get("Pack", {})
        if not pack:  # pragma: no cover
            return
        self.resource.pack_configure(**d.get("Pack", {}))

        logger.debug(f"Ending place for {self.node}")

        x = 1

    @override
    def unplace(self) -> None:
        self.resource.pack_forget()

    @override
    def replace(self, other: Self) -> None:
        _, p = other.node._props.compute()
        other.resource.pack(after=self.resource, **p.get("Pack", {}))

        self.resource.pack_forget()
