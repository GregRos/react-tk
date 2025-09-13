from abc import abstractmethod
from typing import Any, Self, overload

from reactk.model2.util.missing import MISSING


class KeyAccessor[T]:
    type Value = T

    def __str__(self) -> str:
        return f"（ Attribute: {self.key} ）"

    def __bool__(self) -> bool:
        return self.has_key

    @property
    @abstractmethod
    def key(self) -> str: ...

    def __init__(self, target: object) -> None:
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

    @overload
    def get(self, /) -> T: ...

    @overload
    def get[R](self, other: R, /) -> T | R: ...
    def get(self, other: Any = MISSING, /) -> Any:
        if not self.has_key:
            if other is MISSING:
                raise AttributeError(
                    f"{self.target.__class__.__name__} has no {self.key} attribute"
                )
            return other
        return self._get()
