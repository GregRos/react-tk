from collections import defaultdict
from inspect import FrameInfo
import sys
from typing import Any, Callable, ClassVar, Generator, Iterable, Optional

from reactk.model.shadow_node import ShadowNode
from reactk.model.context import Ctx

from reactk.model.top import TopLevelNode
from reactk.model.trace2 import RenderFrame
from reactk.pretty.format_superscript import format_superscript
from reactk.model.trace2 import RenderTrace, RenderTraceAccessor
from reactk.rendering.generate_actions import (
    AnyNode,
    ComputeTreeActions,
    ReconcileAction,
)
from reactk.rendering.reconciler import Reconciler, ReconcilerAccessor
from reactk.rendering.ui_state import RenderState, RenderedNode
from reactk.model.component import Component


def with_trace(node: ShadowNode[Any], trace: RenderTrace) -> ShadowNode[Any]:
    return RenderTraceAccessor(node).set(trace) or node


class ComponentMount[Node: ShadowNode[Any] = ShadowNode[Any]]:
    _mounted: Component[Node]
    state: RenderState

    def __init__(self, mount: Component[Node], context: Ctx | None = None):
        self.context = context or Ctx()
        self.context += lambda _: self.force_rerender()
        self._mounted = mount
        self.state = RenderState(existing_resources={})

    @property
    def _compute_actions(self):
        return ComputeTreeActions(self.state)

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
        self.state.placed = set()
        nodes = [*self._compute_render(self._mounted)]
        top_level_fake = TopLevelNode().__merge__(KIDS=nodes)
        actions = [*self._compute_actions.compute_actions(top_level_fake)]
        self.state.existing_resources[top_level_fake.__uid__] = RenderedNode(
            object(),
            top_level_fake,
        )
        for action in actions:
            Reconciler = ReconcilerAccessor(action.node).get()
            reconciler = Reconciler.create(self.state)
            if not reconciler:
                raise ValueError(
                    f"No reconciler found for action type {type(action.node)}"
                )
            reconciler.run_action(action)
