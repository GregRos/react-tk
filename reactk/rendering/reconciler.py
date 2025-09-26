from abc import abstractmethod
from reactk.rendering.future_actions import (
    Create,
    Place,
    Recreate,
    Replace,
    Unplace,
    Update,
)
from reactk.rendering.generate_actions import AnyNode, ReconcileAction, logger
from reactk.rendering.ui_state import RenderState


from typing import Callable, Iterable, Protocol


class Reconciler[Res]:
    @classmethod
    @abstractmethod
    def create(cls, state: RenderState) -> "Reconciler[Res]": ...
    @abstractmethod
    def run_action(self, action: ReconcileAction[Res]) -> None: ...
