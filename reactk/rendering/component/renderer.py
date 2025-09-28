from collections import defaultdict
from inspect import FrameInfo
import sys
from typing import Any, Callable, ClassVar, Generator, Iterable, Optional

from reactk.model.renderable.node.shadow_node import ShadowNode
from reactk.model.renderable.context import Ctx

from reactk.model.renderable.node.top import TopLevelNode
from reactk.model.renderable.trace import RenderFrame
from reactk.model.renderable.trace import RenderTrace, RenderTraceAccessor
from reactk.rendering.actions.compute import (
    AnyNode,
    ComputeTreeActions,
    ReconcileAction,
)
from reactk.rendering.actions.reconciler import ReconcilerBase, ReconcilerAccessor
from reactk.rendering.actions.reconcile_state import (
    PersistentReconcileState,
    RenderedNode,
    TransientReconcileState,
)
from reactk.model.renderable.component import Component


def _with_trace(node: ShadowNode[Any], trace: RenderTrace) -> ShadowNode[Any]:
    return RenderTraceAccessor(node).set(trace) or node


class RootRenderer[Node: ShadowNode[Any] = ShadowNode[Any]]:
    _mounted: Component[Node]
    state: PersistentReconcileState

    def __init__(self, mount: Component[Node], context: Ctx | None = None):
        self.context = context or Ctx()
        self.context += lambda _: self.force_rerender()
        self._mounted = mount
        self.state = PersistentReconcileState(existing_resources={})

    def _compute_actions(self, transient_state: TransientReconcileState, root):
        return ComputeTreeActions(transient_state).compute_actions(root)

    def __call__(self, **ctx_args: Any):
        self.context(**ctx_args)
        return self.context

    def _render_kids(
        self, node: ShadowNode[Any]
    ) -> Generator[ShadowNode[Any], None, None]:
        for kid in node.KIDS:
            if isinstance(kid, ShadowNode):
                yield kid
            elif isinstance(kid, Component):
                yield from self._compute_render(kid)
            else:
                raise TypeError(
                    f"Expected KIDS to contain ShadowNode or Component, but got {type(kid)}"
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
                        node = node.__merge__(KIDS=tuple(self._render_kids(node)))
                        rendering += (_with_trace(node, my_trace),)
                    elif isinstance(node, Component):
                        node.render(on_yielded_for(my_trace), self.context)  # type: ignore
                    else:
                        raise TypeError(
                            f"Expected render method to return {node_type} or Component, but got {type(node)}"
                        )

            return on_yielded

        yield_ = on_yielded_for(trace)
        yield_(root)
        return rendering

    def force_rerender(self):
        nodes = [*self._compute_render(self._mounted)]
        top_level_fake = TopLevelNode().__merge__(KIDS=nodes)
        self.state.overwrite(RenderedNode(object(), top_level_fake))
        transient_state = self.state.new_transient()
        actions = [*self._compute_actions(transient_state, top_level_fake)]

        for action in actions:
            Reconciler = ReconcilerAccessor(action.node).get()
            reconciler = Reconciler.create(transient_state)
            if not reconciler:
                raise ValueError(
                    f"No reconciler found for action type {type(action.node)}"
                )
            reconciler.run_action(action)
