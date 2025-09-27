from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from reactk.model.shadow_node import ShadowNode

if TYPE_CHECKING:
    from reactk.rendering.generate_actions import AnyNode


@dataclass
class RenderedNode[Res]:
    resource: Res
    node: ShadowNode[Any]

    def migrate(self, node: "AnyNode"):
        self.node = node
        return self


@dataclass
class RenderState:
    existing_resources: dict[str, RenderedNode] = field(default_factory=dict)
    placed: set[str] = field(default_factory=set)
