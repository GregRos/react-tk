from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from react_tk.reflect.accessor.base import KeyAccessor
from react_tk.props.impl import prop
from react_tk.rendering.actions.actions import (
    Compat,
    Create,
    NonCompoundReconcileAction,
    Place,
    ReconcileAction,
    Unplace,
    Update,
)
from react_tk.rendering.actions.compute import AnyNode, logger
from react_tk.rendering.actions.reconcile_state import (
    PersistentReconcileState,
    RenderedNode,
    TransientReconcileState,
)


from typing import Callable, Iterable, Protocol


@dataclass
class ReconcilerBase[Res](ABC):
    state: PersistentReconcileState

    def _register(self, node: AnyNode, resource: Res) -> RenderedNode[Res]:
        rendered = RenderedNode(resource, node)
        self.state.existing_resources[node.__uid__] = rendered
        return rendered

    @classmethod
    @abstractmethod
    def get_compatibility(cls, older: RenderedNode[Res], newer: AnyNode) -> Compat: ...

    @classmethod
    @abstractmethod
    def create(cls, state: TransientReconcileState) -> "ReconcilerBase[Res]": ...

    @abstractmethod
    def run_action(self, action: NonCompoundReconcileAction[Res]) -> None: ...


class ReconcilerAccessor(KeyAccessor[type[ReconcilerBase]]):
    @property
    def key(self) -> str:
        return "_reconciler"


reconciler = ReconcilerAccessor.decorate
