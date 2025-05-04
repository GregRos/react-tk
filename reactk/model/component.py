from __future__ import annotations
import abc
from dataclasses import dataclass, field
import threading
from time import sleep
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    ClassVar,
    Generator,
    Iterable,
    NotRequired,
    Self,
    Tuple,
    TypedDict,
    Unpack,
    override,
)


from .props.prop import Prop
from .props.prop_dict import PropDict
from .shadow_node import (
    InitPropsBase,
    ShadowNode,
    ShadowProps,
)
from .context import Ctx, Ctx


class ComponentProps(InitPropsBase):
    key: Annotated[NotRequired[str], Prop(no_value="")]
    children: Annotated[NotRequired[Tuple[Self, ...]], Prop(no_value=())]


type RenderResult[Node: ShadowNode] = Component[Node] | Node


@dataclass(kw_only=True)
class Component[Node: ShadowNode](abc.ABC):
    key: str = field(default="")

    def _copy(self, **overrides: Any) -> Self:
        return self.__class__(**{**self.__dict__, **overrides})

    def render(self, yld: Callable[[Any], None], ctx: Ctx, /): ...
