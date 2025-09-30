from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from react_tk.renderable.node.prop_value_accessor import PropValuesAccessor
from react_tk.renderable.node.shadow_node import ShadowNode, ShadowNodeInfo
from react_tk.renderable.trace import RenderTrace, RenderTraceAccessor

if TYPE_CHECKING:
    from react_tk.rendering.actions.compute import AnyNode


@dataclass
class RenderedNode[Res]:
    resource: Res
    node: ShadowNode[Any]

    def __str__(self) -> str:
        return f"®️ {str(self.node)}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def TRACE(self) -> RenderTrace:
        return RenderTraceAccessor(self.node).get()

    def migrate(self, node: "AnyNode"):
        self.node = node
        return self


@dataclass
class PersistentReconcileState:
    existing_resources: dict[str, RenderedNode] = field(default_factory=dict)
    placed_resources: set[str] = field(default_factory=set)

    def overwrite(self, rendered: RenderedNode) -> None:
        self.existing_resources[rendered.node.__uid__] = rendered
        self.placed_resources.add(rendered.node.__uid__)

    def new_transient(self) -> "TransientReconcileState":
        return TransientReconcileState(
            existing_resources=self.existing_resources,
            placed_resources=self.placed_resources,
        )

    def __getitem__(self, node: ShadowNode[Any]) -> RenderedNode:
        return self.existing_resources[node.__uid__]

    def get(self, node: ShadowNode[Any]) -> RenderedNode | None:
        return self.existing_resources.get(node.__uid__, None)


@dataclass
class TransientReconcileState(PersistentReconcileState):
    placing: set[str] = field(default_factory=set)
