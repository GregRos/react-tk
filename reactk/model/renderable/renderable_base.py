from abc import ABC
import sys
from typing import Any

from reactk.model.renderable.trace import ConstructTraceAccessor
from reactk.util.stack import get_first_non_init_frame_info


class RenderableBase(ABC):
    def __init__(self, *_: Any, **__: Any) -> None:
        caller = get_first_non_init_frame_info()
        ConstructTraceAccessor(self).set(caller)
