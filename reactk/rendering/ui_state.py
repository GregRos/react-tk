from dataclasses import dataclass, field
from typing import Any, Mapping
from reactk.model.resource import Resource
from reactk.model.shadow_node import ShadowNode


type NodeMapping = Mapping[type[ShadowNode[Any]], type[Resource]]


@dataclass
class RenderState:
    node_mapping: NodeMapping
    existing_resources: dict[str, Resource] = field(default_factory=dict)
    placed: set[str] = field(default_factory=set)
