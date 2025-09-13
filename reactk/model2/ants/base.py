from dataclasses import dataclass
from typing import Any

from reactk.model2.ants.key_accessor import KeyAccessor


@dataclass(unsafe_hash=True, eq=True)
class Reader_Base:
    target: Any

    def __str__(self) -> str:
        return str(self.target)

    def access(self, accessor: type[KeyAccessor[Any]]) -> KeyAccessor[Any]:
        return accessor(self.target)
