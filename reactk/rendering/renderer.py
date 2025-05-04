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

    def _compute_render(self):
        rendering = ()
        trace = RenderTrace()

        def on_yielded_for(base_trace: RenderTrace):
            occurence_by_line = defaultdict(lambda: 1)

            def on_yielded(
                node: Component[X] | X | Iterable[X] | Iterable[Component[X]],
            ):
                caller = sys._getframe(1)
                line_no = caller.f_lineno
                nodes = list(node) if isinstance(node, Iterable) else [node]
                for node in nodes:
                    node_type = self._reconciler.node_type
                    nonlocal rendering
                    my_trace = base_trace + RenderFrame(
                        node, line_no, occurence_by_line[line_no]
                    )
                    occurence_by_line[line_no] += 1

                    if isinstance(node, node_type):  # type: ignore
                        rendering += (with_trace(node, my_trace),)
                    elif isinstance(node, Component):
                        node.render(on_yielded_for(my_trace), self.context)
                    else:
                        raise TypeError(
                            f"Expected render method to return {node_type} or Component, but got {type(node)}"
                        )

            return on_yielded

        yield_ = on_yielded_for(trace)
        yield_(self._mounted)
        return rendering

    def remount(self, root: Component[X]):
        self._mounted = root
        self.force_rerender()

    def force_rerender(self):
        self._reconciler.reconcile(self._compute_render())
