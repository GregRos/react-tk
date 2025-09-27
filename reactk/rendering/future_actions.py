from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any


from reactk.model.prop_value_accessor import PropValuesAccessor
from reactk.model2.prop_model.prop import Prop_ComputedMapping
from reactk.rendering.ui_state import RenderedNode

if TYPE_CHECKING:
    from reactk.rendering.generate_actions import AnyNode


@dataclass
class Create[Res]:
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
class Update[Res]:
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
class Recreate[Res]:
    old: RenderedNode[Res]
    next: "AnyNode"
    container: "AnyNode"

    def node(self) -> "AnyNode":
        return self.next

    def __post_init__(self):
        self.diff = PropValuesAccessor(self.next).get().compute()

    @property
    def props(self):
        return f"{self.old.node.__uid__} ♻️ {PropValuesAccessor(self.next).get()}"

    @property
    def key(self) -> Any:
        return self.next.__uid__

    @property
    def is_creating_new(self) -> bool:
        return True


@dataclass
class Place[Res]:
    container: "AnyNode"
    at: int
    what: Update[Res] | Recreate[Res] | Create[Res]

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
class Replace[Res]:
    container: "AnyNode"
    replaces: RenderedNode[Res]
    with_what: Update | Recreate | Create

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


@dataclass
class Unplace[Res]:
    what: RenderedNode[Res]
    container: "AnyNode"

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
