from abc import ABC, abstractmethod
from dataclasses import dataclass
from reactk.model2.ants.key_accessor import KeyAccessor
from reactk.model2.prop_model import prop
from reactk.rendering.future_actions import (
    Create,
    Place,
    Recreate,
    Replace,
    Unplace,
    Update,
)
from reactk.rendering.generate_actions import AnyNode, ReconcileAction, logger
from reactk.rendering.ui_state import RenderState, RenderedNode


from typing import Callable, Iterable, Protocol


@dataclass
class Reconciler[Res](ABC):
    state: RenderState

    def _register(self, node: AnyNode, resource: Res) -> RenderedNode[Res]:
        rendered = RenderedNode(resource, node)
        self.state.existing_resources[node.__uid__] = rendered
        return rendered

    @classmethod
    @abstractmethod
    def get_compatibility(cls, older: AnyNode, newer: AnyNode) -> str: ...

    @classmethod
    @abstractmethod
    def create(cls, state: RenderState) -> "Reconciler[Res]": ...

    @abstractmethod
    def run_action(self, action: ReconcileAction[Res]) -> None: ...


class ReconcilerAccessor(KeyAccessor[type[Reconciler]]):
    @property
    def key(self) -> str:
        return "_reconciler"


reconciler = ReconcilerAccessor.decorate
