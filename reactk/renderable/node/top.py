from typing import Any, Unpack

from reactk.renderable.node.shadow_node import NodeProps, ShadowNode
from reactk.props.annotations.decorators import schema_setter


# does not need a reconciler since it is never diffed or updated
class TopLevelNode(ShadowNode[Any]):
    @schema_setter()
    def __init__(self, **props: Unpack[NodeProps]) -> None: ...

    @property
    def __uid__(self) -> str:
        return "top"
