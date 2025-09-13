from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

from reactk.model2.ants.key_accessor import KeyAccessor

if TYPE_CHECKING:
    from reactk.model2.ants.reflector import Reflector


@dataclass(unsafe_hash=True, eq=True)
class Reader_Base:
    target: Any
    reflector: Reflector

    def __str__(self) -> str:
        return str(self.target)

    def access(self, accessor: type[KeyAccessor[Any]]) -> KeyAccessor[Any]:
        return accessor(self.target)
