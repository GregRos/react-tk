from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from reactk.model.renderable.node.prop_value_accessor import PropValuesAccessor
from reactk.model.renderable.node.shadow_node import ShadowNode
from reactk.model.renderable.trace import RenderTrace, RenderTraceAccessor

if TYPE_CHECKING:
    from reactk.rendering.actions.compute import AnyNode


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
class PersistentReconcileState:
    existing_resources: dict[str, RenderedNode] = field(default_factory=dict)

    def overwrite(self, rendered: RenderedNode) -> None:
        self.existing_resources[rendered.node.__uid__] = rendered

    def new_transient(self) -> "TransientReconcileState":
        return TransientReconcileState(existing_resources=self.existing_resources)


@dataclass
class TransientReconcileState(PersistentReconcileState):
    placed: set[str] = field(default_factory=set)
