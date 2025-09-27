from collections import defaultdict
from inspect import FrameInfo
import sys
from typing import Any, Callable, ClassVar, Generator, Iterable, Optional

from reactk.model import ShadowNode, Ctx, Component
from reactk.model.top import TopLevelNode
from reactk.model.trace.render_frame import RenderFrame
from reactk.pretty.format_superscript import format_superscript
from reactk.model.trace.render_trace import RenderTrace
from reactk.rendering.generate_actions import (
    AnyNode,
    ComputeTreeActions,
    ReconcileAction,
)
from reactk.rendering.reconciler import Reconciler
from reactk.rendering.ui_state import RenderState


def with_trace(node: ShadowNode[Any], trace: RenderTrace) -> ShadowNode[Any]:
    return node.__merge__(__TRACE__=trace)


class ComponentMount[Node: ShadowNode[Any] = ShadowNode[Any]]:
    _mounted: Component[Node]
    state: RenderState

    def __init__(self, mount: Component[Node], context: Ctx | None = None):
        self.context = context or Ctx()
        self._mounted = mount
        self.state = RenderState(existing_resources={})
        self.mount(mount)

    @property
    def _compute_actions(self):
        return ComputeTreeActions(self.state)

    def __call__(self, **ctx_args: Any):
        self.context(**ctx_args)
        return self.context

    def _render_kids(
        self, node: ShadowNode[Any]
    ) -> Generator[ShadowNode[Any], None, None]:
        for kid in node.__CHILDREN__:
            if isinstance(kid, ShadowNode):
                yield kid
            elif isinstance(kid, Component):
                yield from self._compute_render(kid)
            else:
                raise TypeError(
                    f"Expected __CHILDREN__ to contain ShadowNode or Component, but got {type(kid)}"
                )

    def _compute_render(self, root: Component[Node]) -> tuple[ShadowNode[Any], ...]:
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
                        node.__merge__(__CHILDREN__=(*self._render_kids(node),))
                        rendering += (with_trace(node, my_trace),)
                    elif isinstance(node, Component):
                        node.render(on_yielded_for(my_trace), self.context)
                    else:
                        raise TypeError(
                            f"Expected render method to return {node_type} or Component, but got {type(node)}"
                        )

            return on_yielded

        yield_ = on_yielded_for(trace)
        yield_(root)
        return rendering

    def mount(self, root: Component[Any]):
        self._mounted = root
        self.force_rerender()

    def force_rerender(self):
        nodes = self._compute_render(self._mounted)
        actions = self._compute_actions.compute_actions(TopLevelNode()[*nodes])
        reconciler_dict = dict()

        for action in actions:
            Reconciler = action.node.get_reconciler()
            reconciler = Reconciler.create(self.state)
            if not reconciler:
                raise ValueError(
                    f"No reconciler found for action type {type(action.node)}"
                )
            reconciler.run_action(action)
