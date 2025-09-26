from typing import Any
from reactk.model.resource import Compat
from reactk.model.shadow_node import ShadowNode


class TopLevelNode(ShadowNode[Any]):
    def get_compatibility(self, other: ShadowNode[Any]) -> Compat:
        return "update"

    pass
