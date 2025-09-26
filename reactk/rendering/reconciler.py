from abc import abstractmethod
from reactk.model import Resource
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


class Reconciler[Res](Protocol):
    @abstractmethod
    def run_action(action: ReconcileAction[Res]) -> None: ...
