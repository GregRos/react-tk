from ast import List
from collections import defaultdict
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
import sys
from typing import Any, Iterable, overload
from reactk.model.renderable.component import (
    AbsCtx,
    AbsSink,
    Component,
    RenderElement,
    RenderResult,
    is_render_element,
)
from reactk.model.renderable.context import Ctx
from reactk.model.renderable.node.shadow_node import ShadowNode
from reactk.model.renderable.trace import (
    ConstructTraceAccessor,
    RenderFrame,
    RenderTrace,
    RenderTraceAccessor,
    SequencedRenderFrame,
)


class RenderState:
    next_render_trace_seq_id: dict[tuple[RenderTrace, RenderFrame], int]

    def __init__(self):
        self.next_render_trace_seq_id = defaultdict(lambda: 0)

    def produce_sequenced(
        self, trace: RenderTrace, frame: RenderFrame
    ) -> SequencedRenderFrame:
        free_seq_id = self.next_render_trace_seq_id[(trace, frame)]
        self.next_render_trace_seq_id[(trace, frame)] += 1
        return frame.to_sequenced(free_seq_id)


@dataclass
class RenderSink[Node: ShadowNode[Any] = ShadowNode[Any]](AbsSink[Node]):
    state: RenderState
    trace_root: RenderTrace
    ctx: Ctx
    rendered: list[Node] = field(default_factory=list, init=False)

    def _get_construct_trace(self, node: RenderElement[Node]):
        if not is_render_element[Node](node):
            raise TypeError(
                f"Expected node to be ShadowNode or Component, but got {type(node)}"
            )
        construct_trace = ConstructTraceAccessor(node).get(None)

        if not construct_trace:
            raise RuntimeError(
                f"Expected {node.__class__} to have a construct trace, but it was missing"
            )
        return construct_trace

    def _child_sink(self, trace: RenderTrace) -> "RenderSink[Node]":
        return RenderSink(
            state=self.state,
            trace_root=trace,
            ctx=self.ctx,
        )

    def _send_one(self, node: RenderElement[Node]) -> None:
        construct_trace = self._get_construct_trace(node)
        frame_base = RenderFrame.create(node, construct_trace)
        sequenced = self.state.produce_sequenced(self.trace_root, frame_base)
        new_trace = self.trace_root + sequenced
        RenderTraceAccessor(node).set(new_trace)
        new_sink = self._child_sink(new_trace)
        match node:
            case ShadowNode():
                new_sink.push(node.KIDS)
                node = node.__merge__(KIDS=tuple(new_sink.rendered))
                self.rendered.append(node)
            case Component():
                new_sink._run_component_render(node)
                self.rendered.extend(new_sink.rendered)
            case _:
                raise TypeError(
                    f"Expected node to be ShadowNode or Component, but got {type(node)}"
                )

    def push(self, node: RenderResult[Node], /) -> None:
        nodes = list(node) if isinstance(node, Iterable) else [node]
        for node in nodes:
            self._send_one(node)

    def _run_component_render(self, component: Component[Node]) -> None:
        component.__sink__ = self
        component.render()

    def _run_render(self, component: RenderElement[Node]) -> Iterable[Node]:
        if isinstance(component, ShadowNode):
            self._run_component_render(component)

    def run(self, component: "RenderElement[Node]") -> Iterable[Node]:
        self._run_render(component)
        return self.rendered


@dataclass
class RenderEnv[Node: ShadowNode[Any] = ShadowNode[Any]]:
    sink: AbsSink[Node]
    component: Component[Node]

    def __enter__(self) -> Component[Node]:
        self.component.__sink__ = self.sink
        return self.component

    def __exit__(self, *args: Any) -> None:
        self.component.__sink__ = None  # type: ignore
