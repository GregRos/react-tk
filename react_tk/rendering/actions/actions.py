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


@dataclass
class Replace[Res = Misc]:
    container: "AnyNode"
    replaces: RenderedNode[Res]
    with_what: Update[Res] | Create[Res]
    at: int

    @property
    def node(self) -> "AnyNode":
        return self.with_what.next

    @property
    def is_creating_new(self) -> bool:
        return self.with_what.is_creating_new

    @property
    def diff(self) -> Prop_ComputedMapping:
        return self.with_what.diff

    def __repr__(self) -> str:
        return f"{self.replaces.node.__uid__} ↔️ {self.with_what.__repr__()}"

    @property
    def uid(self) -> Any:
        return self.replaces.node.__uid__


type SubAction[T = Misc] = Update[T] | Create[T]
type ReconcileAction[Res = Misc] = Place[Res] | Unplace[Res] | Update[Res] | Replace[
    Res
]


type Compat = Literal["update", "switch", "place"]
