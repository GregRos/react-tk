from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

# Compat moved here from reactk.model.resource to centralize reconciler types
from reactk.reflect.accessor.base import KeyAccessor
from reactk.model.props.impl import prop
from reactk.rendering.actions.actions import (
    Create,
    Place,
    Recreate,
    Replace,
    Unplace,
    Update,
)
from reactk.rendering.actions.compute import AnyNode, ReconcileAction, logger
from reactk.rendering.render_state import RenderState, RenderedNode


from typing import Callable, Iterable, Protocol

type Compat = Literal["update", "replace", "recreate"]


@dataclass
class ReconcilerBase[Res](ABC):
    state: RenderState

    def _register(self, node: AnyNode, resource: Res) -> RenderedNode[Res]:
        rendered = RenderedNode(resource, node)
        self.state.existing_resources[node.__uid__] = rendered
        return rendered

    @classmethod
    @abstractmethod
    def get_compatibility(cls, older: RenderedNode[Res], newer: AnyNode) -> Compat: ...

    @classmethod
    @abstractmethod
    def create(cls, state: RenderState) -> "ReconcilerBase[Res]": ...

    @abstractmethod
    def run_action(self, action: ReconcileAction[Res]) -> None: ...


class ReconcilerAccessor(KeyAccessor[type[ReconcilerBase]]):
    @property
    def key(self) -> str:
        return "_reconciler"


reconciler = ReconcilerAccessor.decorate
