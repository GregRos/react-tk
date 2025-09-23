from typing import Any, ClassVar, Self
from reactk.model.resource import Compat, Resource
from reactk.model.shadow_node import ShadowNode
from reactk.model2.prop_model.prop import Prop_ComputedMapping
from reactk.rendering.generate_actions import AnyNode
from reactk.tk.window import Window


class TopNode(ShadowNode):
    INSTANCE: ClassVar["TopNode"]

    def __new__(cls, *args, **kwargs):
        if cls.INSTANCE is None:
            cls.INSTANCE = super().__new__(cls)
        return cls.INSTANCE


class TopLevelVirtualResource(Resource[TopNode]):
    INSTANCE: ClassVar["TopLevelVirtualResource"]

    def __new__(cls, *args, **kwargs):
        if cls.INSTANCE is None:
            cls.INSTANCE = super().__new__(cls)
        return cls.INSTANCE

    def is_same_resource(self, other: Any) -> bool:
        return True

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
        return cls()
