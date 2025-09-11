from abc import ABC
from dataclasses import dataclass, field
from typing import Annotated, Any, Callable, NotRequired, Self, Tuple

from reactk.model.context import Ctx
from reactk.model2.prop_model.c_meta import prop_meta
from reactk.model2.rendering_model.s_node import InitPropsBase, ShNode


class ComponentProps(InitPropsBase):
    key: Annotated[NotRequired[str], prop_meta(no_value="")]


type RenderResult[Node: ShNode] = Comp[Node] | Node


@dataclass(kw_only=True)
class Comp[Node: ShNode](ABC):
    key: str = field(default="")

    def render(self, yld: Callable[[RenderResult[Node]], None], ctx: Ctx, /): ...
