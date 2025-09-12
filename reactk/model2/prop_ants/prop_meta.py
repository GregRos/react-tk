from abc import abstractmethod
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Concatenate,
    Iterable,
    Mapping,
    Protocol,
    Self,
    overload,
)

from reactk.model2.ants.annotations import OrigAccessor
from reactk.model2.prop_model.common import (
    IS_REQUIRED,
    Converter,
    DiffMode,
    KeyedValues,
)
from reactk.model2.prop_ants.create_props import MetaAccessor
from reactk.model2.prop_ants.decorators import (
    _HasMerge,
    MethodSetterTransformer,
    schema_setter,
    prop_setter,
    _getter,
    prop_getter,
    HasChildren,
)

if TYPE_CHECKING:
    from reactk.model2.prop_model.prop import (
        Prop,
        PropBlock,
        SomeProp,
        PropBlockValues,
        SomePropValue,
    )


@dataclass(kw_only=True)
class common_meta:
    metadata: dict[str, Any] = {}
    repr: DiffMode = "recursive"
    name: str | None = None


@dataclass(kw_only=True)
class prop_meta(common_meta):
    subsection: str | None = None
    no_value: Any = IS_REQUIRED
    converter: Converter[Any] | None = None


@dataclass(kw_only=True)
class schema_meta(common_meta):
    pass


# moved decorator and helper types live in decorators.py


type some_meta = prop_meta | schema_meta
