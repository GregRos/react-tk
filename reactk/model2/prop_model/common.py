from collections.abc import Mapping
from typing import Any, Callable, Literal


type Converter[T] = Callable[[T], Any]


class _IS_REQUIRED_TYPE:
    pass


type DiffMode = Literal["simple", "recursive", "never"]

IS_REQUIRED = _IS_REQUIRED_TYPE()

type KeyedValues = Mapping[str, Any]
