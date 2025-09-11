from dataclasses import dataclass
from typing import Any

from reactk.model2.prop_model.coommon import IS_REQUIRED, Converter, DiffMode


@dataclass(kw_only=True)
class common_meta:
    metadata: dict[str, Any] = {}
    repr: DiffMode = "recursive"


@dataclass(kw_only=True)
class prop_meta(common_meta):
    no_value: Any = IS_REQUIRED
    converter: Converter[Any] | None = None


@dataclass(kw_only=True)
class schema_meta(common_meta):
    pass
