from typing import Any
from reactk.model.context import Ctx
from reactk.rendering.renderer import ComponentMount
from reactk.rendering.stateful_reconciler import StatefulReconciler
from reactk.model.component import Component
from reactk.tk.window_wrapper import WindowWrapper
from reactk.tk.window import Window


class WindowMount(ComponentMount[Window]):
    def __init__(self, root: Component):
        self._ctx = Ctx()
        reconciler = StatefulReconciler[Window](
            WindowWrapper, lambda x: WindowWrapper.create(x, self._ctx)
        )
        super().__init__(reconciler, self._ctx, root)
        self.context += lambda _: self.force_rerender()
