from typing import Any

from reactk.model.renderable.node.shadow_node import NodeProps, ShadowNode
from reactk.model.props.annotations.decorators import schema_setter


# does not need a reconciler since it is never diffed or updated
class TopLevelNode(ShadowNode[Any]):
    @schema_setter()
    def __init__(self, **props: NodeProps) -> None: ...

    @property
    def __uid__(self) -> str:
        return "top"
