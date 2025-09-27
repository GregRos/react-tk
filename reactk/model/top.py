from typing import Any
from reactk.model.resource import Compat
from reactk.model.shadow_node import NodeProps, ShadowNode
from reactk.model2.prop_ants.decorators import schema_setter


class TopLevelNode(ShadowNode[Any]):
    @schema_setter()
    def __init__(self, **props: NodeProps) -> None: ...
    def _get_compatibility(self, other: ShadowNode[Any]) -> Compat:
        return "update"

    @property
    def __uid__(self) -> str:
        return "top"

    @classmethod
    def get_reconciler(cls):
        from reactk.model.top_reconciler import TopLevelReconciler

        return TopLevelReconciler
