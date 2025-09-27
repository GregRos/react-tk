from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from reactk.model.prop_value_accessor import PropValuesAccessor
from reactk.model.shadow_node import ShadowNode
from reactk.model.trace.render_trace import RenderTrace, RenderTraceAccessor

if TYPE_CHECKING:
    from reactk.rendering.generate_actions import AnyNode


@dataclass
class RenderedNode[Res]:
    resource: Res
    node: ShadowNode[Any]

    @property
    def TRACE(self) -> RenderTrace:
        return RenderTraceAccessor(self.node).get()

    def migrate(self, node: "AnyNode"):
        self.node = node
        return self


@dataclass
class RenderState:
    existing_resources: dict[str, RenderedNode] = field(default_factory=dict)
    placed: set[str] = field(default_factory=set)
