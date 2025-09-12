from typing import Any, TypeVar

from reactk.model2.ants.key_accessor import KeyAccessor


class ArgsAccessor(KeyAccessor[tuple]):
    """Accessor for the private __args__ attribute used by typing.

    This accessor raises an AttributeError if the attribute is missing to
    make callers handle the absence explicitly (per new API requirement).
    """

    @property
    def key(self) -> str:
        return "__args__"


class TypeParamsAccessor(KeyAccessor[tuple[TypeVar, ...]]):
    """Accessor for the private __type_params__ attribute.

    Returns a tuple of TypeVar objects when present, or an empty tuple if
    the attribute is absent. The return type is annotated as
    tuple[TypeVar, ...].
    """

    @property
    def key(self) -> str:
        return "__type_params__"
