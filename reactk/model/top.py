from typing import Any
from reactk.model.resource import Compat
from reactk.model.shadow_node import ShadowNode


class TopLevelNode(ShadowNode[Any]):
    def _get_compatibility(self, other: ShadowNode[Any]) -> Compat:
        return "update"

    @property
    def __uid__(self) -> str:
        return "top"

    @classmethod
    def get_reconciler(cls):
        from reactk.model.top_reconciler import TopLevelReconciler

        return TopLevelReconciler
