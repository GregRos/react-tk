from collections import defaultdict
from inspect import FrameInfo
import sys
from typing import Any, Callable, Generator, Iterable

from reactk.model import ShadowNode, Ctx, Component
from reactk.model.trace.render_frame import RenderFrame
from reactk.pretty.format_superscript import format_superscript
from reactk.model.trace.render_trace import RenderTrace
from reactk.rendering.generate_actions import AnyNode, ComputeTreeActions
from reactk.rendering.ui_state import NodeMapping, RenderState


def with_trace(node: ShadowNode[Any], trace: RenderTrace) -> ShadowNode[Any]:
    return node.__merge__(trace=trace)


class ComponentMount:
    _mounted: Component[AnyNode]
    state: RenderState

    def __init__(self, context: Ctx, node_mapping: NodeMapping):
        self.context = context
        self.state = RenderState(existing_resources={}, node_mapping=node_mapping)

    @property
    def _compute_actions(self):
        return ComputeTreeActions(self.state)

    def __call__(self, **ctx_args: Any):
        self.context(**ctx_args)
        return self.context

    def _compute_render(self) -> None:
        rendering = tuple[ShadowNode[Any], ...]()
        trace = RenderTrace()

        def on_yielded_for(base_trace: RenderTrace):
            occurence_by_line = defaultdict(lambda: 1)

            def on_yielded(
                node: (
                    Component[Any]
                    | ShadowNode[Any]
                    | Iterable[ShadowNode[Any]]
                    | Iterable[Component[AnyNode]]
                ),
            ):
                caller = sys._getframe(1)
                line_no = caller.f_lineno
                nodes = list(node) if isinstance(node, Iterable) else [node]
                for node in nodes:
                    nonlocal rendering
                    my_trace = base_trace + RenderFrame(
                        node, line_no, occurence_by_line[line_no]
                    )
                    occurence_by_line[line_no] += 1

                    if isinstance(node, ShadowNode):
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

    def remount(self, root: Component[Any]):
        self._mounted = root
        self.force_rerender()

    def force_rerender(self):
        nodes = self._compute_render()
        actions = self._compute_actions.compute_actions(nodes)
        self._reconciler.reconcile(actions)
