from abc import ABC
from dataclasses import dataclass, field
from typing import Annotated, Any, Callable, NotRequired, Self, Tuple

from reactk.model.context import Ctx
from reactk.model.shadow_node import InitPropsBase, ShadowNode


type RenderResult[Node: ShadowNode] = Component[Node] | Node


@dataclass(kw_only=True)
class Component[Node: ShadowNode](ABC):
    key: str = field(default="")

    def render(self, yld: Callable[[RenderResult[Node]], None], ctx: Ctx, /): ...
