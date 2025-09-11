from collections import defaultdict
from inspect import FrameInfo
import sys
from typing import Any, Callable, Generator, Iterable

from reactk.model import ShadowNode, Ctx, Component
from reactk.model.trace.render_frame import RenderFrame
from reactk.rendering.stateful_reconciler import StatefulReconciler
from reactk.pretty.format_superscript import format_superscript
from reactk.model.trace.render_trace import RenderTrace


def with_trace(node: ShadowNode, trace: RenderTrace) -> ShadowNode:
    return node._copy(trace=trace)


class ComponentMount[X: ShadowNode]:
    _reconciler: StatefulReconciler
    _mounted: Component

    def __init__(
        self, reconciler: StatefulReconciler, context: Ctx, root: Component[X]
    ):
        self._reconciler = reconciler
        self.context = context
        self._mounted = root

    def __call__(self, **ctx_args: Any):
        self.context(**ctx_args)
        return self.context

    def remount(self, root: Component[X]):
        self._mounted = root
        self.force_rerender()

    def force_rerender(self):
        self._reconciler.reconcile(self._compute_render())
