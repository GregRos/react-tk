from dataclasses import dataclass
from typing import Any

from reactk.model2.prop_model.common import KeyedValues

from reactk.model2.prop_model import PValues

from ..model import Resource, ShadowNode


@dataclass
class Create:
    next: ShadowNode

    def __repr__(self) -> str:
        return f"🆕 {self.next}"

    @property
    def key(self) -> Any:
        return self.next.uid


@dataclass
class Update:
    existing: Resource
    next: ShadowNode
    diff: PValues

    def __bool__(self):
        return bool(self.diff)

    def __repr__(self) -> str:
        return f"📝 {self.diff.__repr__()}"

    @property
    def key(self) -> Any:
        return self.next.uid


@dataclass
class Recreate:
    old: Resource
    next: ShadowNode

    @property
    def props(self):
        return f"{self.old.uid} ♻️ {self.next.__PROP_VALUES__}"

    @property
    def key(self) -> Any:
        return self.next.uid


@dataclass
class Place:
    what: Update | Recreate | Create

    def __repr__(self) -> str:
        return f"👇 {self.what.__repr__()}"

    @property
    def uid(self) -> Any:
        return self.what.key


@dataclass
class Replace:
    replaces: Resource
    with_what: Update | Recreate | Create

    def __repr__(self) -> str:
        return f"{self.replaces.uid} ↔️ {self.with_what.__repr__()}"

    @property
    def uid(self) -> Any:
        return self.replaces.uid


@dataclass
class Unplace:
    what: Resource

    def __repr__(self) -> str:
        return f"🙈  {self.what.uid}"

    @property
    def uid(self) -> Any:
        return self.what.uid
