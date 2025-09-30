from dataclasses import dataclass, field
from tkinter import Misc
from typing import TYPE_CHECKING, Any, Iterable, Iterator
from typing_extensions import Literal

from funcy import first


from react_tk.renderable.node.prop_value_accessor import PropValuesAccessor
from react_tk.props.impl.prop import Prop_ComputedMapping
from react_tk.rendering.actions.reconcile_state import RenderedNode

if TYPE_CHECKING:
    from react_tk.rendering.actions.compute import AnyNode


class ConstructiveAction:
    pass


@dataclass
class Create[Res](ConstructiveAction):
    next: "AnyNode"
    container: "AnyNode"

    @property
    def node(self) -> "AnyNode":
        return self.next

    def __post_init__(self):
        self.diff = PropValuesAccessor(self.next).get().compute()

    def __repr__(self) -> str:
        return f"🆕 {self.next}"

    @property
    def key(self) -> Any:
        return self.next.__uid__

    @property
    def is_creating_new(self) -> bool:
        return True


@dataclass
class Update[Res = Misc](ConstructiveAction):
    existing: RenderedNode[Res]
    next: "AnyNode"
    diff: Prop_ComputedMapping

    @property
    def node(self) -> "AnyNode":
        return self.next

    def __bool__(self):
        return bool(self.diff)

    def __repr__(self) -> str:
        return f"📝 {self.diff.__repr__()}"

    @property
    def key(self) -> Any:
        return self.next.__uid__

    @property
    def is_creating_new(self) -> bool:
        return False


@dataclass
class Place[Res = Misc](ConstructiveAction):
    container: "AnyNode"
    at: int
    what: Update[Res] | Create[Res]

    @property
    def node(self) -> "AnyNode":
        return self.what.next

    @property
    def diff(self) -> Prop_ComputedMapping:
        return self.what.diff

    def __repr__(self) -> str:
        return f"👇 {self.what.__repr__()}"

    @property
    def uid(self) -> Any:
        return self.what.key

    @property
    def is_creating_new(self) -> bool:
        return self.what.is_creating_new


@dataclass
class Unplace[Res = Misc]:
    what: RenderedNode[Res]

    @property
    def node(self) -> "AnyNode":
        return self.what.node

    @property
    def is_creating_new(self) -> bool:
        return False

    def __repr__(self) -> str:
        return f"🙈  {self.what.node.__uid__}"

    @property
    def uid(self) -> Any:
        return self.what.node.__uid__


type SubAction[T = Misc] = Update[T] | Create[T]
type ReconcileAction[Res = Misc] = Place[Res] | Unplace[Res] | Update[Res] | Compound[
    Res
]
type NonCompoundReconcileAction[Res = Misc] = Place[Res] | Unplace[Res] | Update[Res]


class Compound[Res](Iterable[ReconcileAction[Res]]):
    def __iter__(self) -> Iterator[ReconcileAction[Res]]:
        return iter(self.actions)

    @property
    def node(self) -> "AnyNode":
        constructive_node = first(
            action.node
            for action in self.actions
            if isinstance(action, ConstructiveAction)
        )
        if not constructive_node:
            raise ValueError("No constructive action found")
        return constructive_node

    def __init__(self, *actions: ReconcileAction[Res]) -> None:
        self.actions = actions

    @property
    def is_creating_new(self) -> bool:
        return any(action.is_creating_new for action in self.actions)


type Compat = Literal["update", "recreate", "place"]
