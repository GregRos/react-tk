from tkinter import Tk
from reactk.model.context import Ctx
from reactk.rendering.renderer import ComponentMount
from reactk.rendering.stateful_reconciler import StatefulReconciler
from reactk.model.component import Component
from reactk.tk.widget import Widget
from reactk.tk.widget_wrapper import WidgetWrapper
from .logger import logger


class WidgetMount(ComponentMount[Widget]):
    def __init__(self, tk: Tk, context: Ctx, root: Component):
        logger.info(f"Creating WidgetMount with root: {root}")
        reconciler = StatefulReconciler[Widget](
            WidgetWrapper, lambda x: WidgetWrapper.create(tk, x)
        )
        super().__init__(reconciler, context, root)
