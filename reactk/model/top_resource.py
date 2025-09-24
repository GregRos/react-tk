from typing import Any, ClassVar, Self
from reactk.model.resource import Compat, Resource
from reactk.model.shadow_node import ShadowNode
from reactk.model2.prop_model.prop import Prop_ComputedMapping
from reactk.rendering.generate_actions import AnyNode
from reactk.tk.window import Window


class VirtualResource[Node: ShadowNode[Any]](Resource[Node]):
    def __init__(self, node: Node):
        super().__init__(node)

    def is_same_resource(self, other: "VirtualResource.ThisResource") -> bool:
        return other.node.uid == self.node.uid

    def migrate(self, node: Any) -> Self:
        return self

    def destroy(self) -> None:
        pass

    def update(self, props: Prop_ComputedMapping) -> None:
        pass

    def place(
        self,
        container: Any,
        props: Prop_ComputedMapping,
        at: int,
    ) -> None:
        pass

    def unplace(self) -> None:
        pass

    def replace(self, other: Any, diff: Prop_ComputedMapping) -> None:
        pass

    def get_compatibility(self, other: Any) -> Compat:
        return "update"

    @classmethod
    def create(cls, container: Any, node: Any) -> Any:
        return cls(node)
