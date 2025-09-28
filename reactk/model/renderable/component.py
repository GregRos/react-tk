from abc import ABC
from collections.abc import Iterable
from dataclasses import dataclass, field
from sre_constants import ANY
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    NotRequired,
    Protocol,
    Self,
    Tuple,
    TypeIs,
    overload,
)

from reactk.model.renderable.node.shadow_node import NodeProps, ShadowNode
from reactk.model.renderable.renderable_base import RenderableBase


type RenderElement[Node: ShadowNode[Any]] = Node | Component[Node]
type RenderResult[Node: ShadowNode[Any] = ShadowNode[Any]] = RenderElement[
    Node
] | Iterable[RenderElement[Node]]


class AbsCtx:
    def __getattr__(self, item: str) -> Any: ...
    def __setattr__(self, key: str, value: Any) -> None: ...


class AbsSink[Node: ShadowNode[Any] = ShadowNode[Any]](Protocol):
    ctx: AbsCtx

    def push(self, node: RenderResult[Node], /) -> None: ...


@dataclass
class InactiveSink[Node: ShadowNode[Any] = ShadowNode[Any]](AbsSink[Node]):
    component_class: type["Component[Node]"]

    @property
    def _component_name(self) -> str:
        return self.component_class.__name__

    @property
    def ctx(self) -> AbsCtx:  # type: ignore
        raise RuntimeError(
            f"Accessed ctx outside of render cycle for {self._component_name}, which is illegal."
        )

    def push(self, node: RenderResult[Node], /) -> None:
        raise RuntimeError(
            f"Pushed nodes outside of render cycle for {self._component_name}, which is illegal."
        )


@dataclass(kw_only=True)
class Component[Node: ShadowNode[Any] = ShadowNode[Any]](RenderableBase, ABC):
    key: str = field(default="")
    __sink__: AbsSink[Any]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        setattr(cls, "__sink__", InactiveSink(cls))

    @property
    def ctx(self) -> AbsCtx:
        return self.__sink__.ctx

    def render(self, /) -> "RenderResult[Node]": ...


@dataclass
class RenderSetup[X: Component[Any]](ABC):
    component: X
    sink: AbsSink
    _original_sink: AbsSink = field(init=False)

    def __enter__(self) -> X:
        self._original_sink = self.component.__sink__
        self.component.__sink__ = self.sink
        return self.component

    def __exit__(self, *args: Any) -> None:
        self.component.__sink__ = self._original_sink


class is_render_element[T: ShadowNode[Any]]:  # type: ignore
    def __new__(cls, obj: Any) -> TypeIs[RenderElement[T]]:
        return isinstance(obj, (ShadowNode, Component))  # type: ignore
