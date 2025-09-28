from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from logging import getLogger
from threading import Lock
import threading
from time import sleep
from typing import Any, Callable, Self

from expression import Nothing

from reactk.model.renderable.component import AbsCtx
from reactk.util.core_reflection import get_attr_skip_hook, has_attr_skip_hook

logger = getLogger("ui")


@dataclass
class CtxLock:
    _parent: "Ctx"

    def __enter__(self):
        self._parent._frozen = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._parent._frozen = False


# FIXME: Multiple issues, including:
# - Weird mutability
# - No type hints (can it be fixed?)
# - Should have consistent ID
# - Consider coolass API for schedule, like ctx(lambda x: x + 1, 10)
# - Probably do away with setattr and leave getattr
# - Improve context equality mechanism
class Ctx(AbsCtx):
    _listeners: list[Callable[[Self], None]] = []
    _map: dict[str, Any] = {}
    _frozen: bool = False

    def __init__(self, **attrs: Any):
        self._map = dict[str, Any](attrs)
        self._listeners = []

    def __getattr__(self, name: str) -> Any:
        attr = get_attr_skip_hook(self, name)
        if not attr is Nothing:
            return attr.value

        return self._map.get(name, None)

    def __iadd__(self, listener: Callable[[Self], Any]) -> Self:
        self._listeners.append(listener)
        return self

    def _notify(self) -> None:
        for listener in self._listeners:
            listener(self)

    def _try_set(self, key: str, value: Any) -> None:
        if has_attr_skip_hook(self, key):
            return super().__setattr__(key, value)

        self._map[key] = value

    def __call__(self, *args: Any, **kwargs: Any) -> Self:
        if args and kwargs:
            raise ValueError("Ctx can be called with either args or kwargs, not both")
        for k, v in kwargs.items():
            self._try_set(k, v)
        self._notify()
        return self

    def __setattr__(self, key: str, value: Any) -> None:
        if has_attr_skip_hook(self, key):
            object.__setattr__(self, key, value)
            return

        self._try_set(key, value)
        self._notify()


def ctx_snapshot(ctx: "Ctx") -> "Ctx":
    return Ctx(**ctx._map.copy())


def ctx_freeze(ctx: "Ctx") -> "CtxLock":
    return CtxLock(ctx)
