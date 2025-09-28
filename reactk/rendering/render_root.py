from typing import Any
from reactk.model.renderable.component import Component
from reactk.model.renderable.context import Ctx, ctx_freeze
from reactk.model.renderable.node.shadow_node import ShadowNode
from reactk.rendering.actions.reconcile_state import PersistentReconcileState
from reactk.rendering.actions.top_reconciler import RootReconciler
from reactk.rendering.component.render_sink import RenderSink, RenderState


class RenderRoot[Node: ShadowNode[Any] = ShadowNode[Any]]:
    _reconciler: RootReconciler[Node]
    _mounted: Component[Node]

    def __init__(self, initial: Component[Node]) -> None:
        self._mounted = initial
        self.ctx = Ctx()
        self.ctx += lambda _: self._rerender()
        self._reconciler = RootReconciler(PersistentReconcileState())

    def __call__(self, **kwargs: Any) -> None:
        self.ctx(**kwargs)

    def _rerender(self):
        with ctx_freeze(self.ctx):
            render_state = RenderState(self.ctx)
            sink = render_state.create_empty_sink()
            render_result = sink.run(self._mounted)
        self._reconciler.reconcile(tuple(render_result))
