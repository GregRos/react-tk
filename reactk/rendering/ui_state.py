from dataclasses import dataclass, field
from typing import Any, Mapping
from reactk.model.shadow_node import ShadowNode
from reactk.rendering.reconciler import Reconciler
from reactk.rendering.future_actions import RenderedNode


type NodeMapping = Mapping[type[ShadowNode[Any]], type[Reconciler[Any]]]


@dataclass
class RenderState:
    reconciler_mapping: NodeMapping
    existing_resources: dict[str, RenderedNode] = field(default_factory=dict)
    placed: set[str] = field(default_factory=set)
