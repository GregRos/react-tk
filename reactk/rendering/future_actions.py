from dataclasses import dataclass, field
from typing import Any

from reactk.model2.prop_model.common import KeyedValues

from reactk.model2.prop_model import Prop_Mapping
from reactk.model2.prop_model.prop import Prop_ComputedMapping

from ..model import Resource, ShadowNode
from ..rendering.generate_actions import AnyNode


@dataclass
class Create:
    next: AnyNode

    def __post_init__(self):
        self.diff = self.next.__PROP_VALUES__.compute()

    def __repr__(self) -> str:
        return f"🆕 {self.next}"

    @property
    def key(self) -> Any:
        return self.next.uid

    @property
    def is_creating_new(self) -> bool:
        return True


@dataclass
class Update:
    existing: Resource
    next: AnyNode
    diff: Prop_ComputedMapping

    def __bool__(self):
        return bool(self.diff)

    def __repr__(self) -> str:
        return f"📝 {self.diff.__repr__()}"

    @property
    def key(self) -> Any:
        return self.next.uid

    @property
    def is_creating_new(self) -> bool:
        return False


@dataclass
class Recreate:
    old: Resource
    next: AnyNode

    def __post_init__(self):
        self.diff = self.next.__PROP_VALUES__.compute()

    @property
    def props(self):
        return f"{self.old.uid} ♻️ {self.next.__PROP_VALUES__}"

    @property
    def key(self) -> Any:
        return self.next.uid

    @property
    def is_creating_new(self) -> bool:
        return True


@dataclass
class Place:
    where: AnyNode
    at: int
    what: Update | Recreate | Create

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
class Replace:
    where: AnyNode
    replaces: Resource
    with_what: Update | Recreate | Create

    @property
    def is_creating_new(self) -> bool:
        return self.with_what.is_creating_new

    @property
    def diff(self) -> Prop_ComputedMapping:
        return self.with_what.diff

    def __repr__(self) -> str:
        return f"{self.replaces.uid} ↔️ {self.with_what.__repr__()}"

    @property
    def uid(self) -> Any:
        return self.replaces.uid


@dataclass
class Unplace:
    what: Resource
    where: AnyNode

    @property
    def is_creating_new(self) -> bool:
        return False

    def __repr__(self) -> str:
        return f"🙈  {self.what.uid}"

    @property
    def uid(self) -> Any:
        return self.what.uid
