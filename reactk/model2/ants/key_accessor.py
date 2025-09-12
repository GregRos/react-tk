from abc import abstractmethod
from typing import Any, Self


class KeyAccessor[T]:
    type Value = T

    @classmethod
    def create(cls, target: Any) -> Self:
        return cls(target)

    def __str__(self) -> str:
        return f"（ Attribute: {self.key} ）"

    @property
    @abstractmethod
    def key(self) -> str: ...

    def __init__(self, target: Any) -> None:
        self.target = target

    def set(self, value: T) -> None:
        try:
            setattr(self.target, self.key, value)
        except Exception:
            pass

    @property
    def has_key(self) -> bool:
        return hasattr(self.target, self.key)

    def _get(self) -> T:

        return getattr(self.target, self.key)

    def get(self) -> T:
        return self._get()
