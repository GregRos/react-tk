from abc import ABC, abstractclassmethod, abstractmethod
from collections.abc import Mapping
from typing import Any, ClassVar, Iterable, Iterator, Optional, Self, Tuple, TypeVar


class VMappingBase[K, V](ABC, Iterable[V]):
    type Input = Iterable[V] | Mapping[K, V]
    """A mapping-like container that is iterable over its value objects.

    - Does NOT subclass collections.abc.Mapping on purpose.
    - Values are expected to carry the key as an attribute named by `_KEY_ATTR`.
    - Subclasses must set `_KEY_ATTR` via `__init_subclass__(key_attr=...)`.

    The constructor accepts either an iterable of V or another VMapping[K, V].
    Internally values are stored in a plain dict mapping keys to values.
    """

    @abstractmethod
    def __iter__(self) -> Iterator[V]: ...

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def __getitem__(self, key: K) -> V: ...

    @abstractmethod
    def _get_key(self, value: V) -> K: ...

    def _to_dict(self, values: Input) -> dict[K, V]:
        """Convert an iterable of values or a mapping to a plain mapping."""
        match values:
            case Mapping() as m:
                return dict(m)  # type: ignore[return-value]
            case _:
                return {self._get_key(v): v for v in values}

    def __contains__(self, key: Any) -> bool:
        try:
            self[key]
            return True
        except KeyError:
            return False

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> Iterable[K]:
        for x in self:
            yield self._get_key(x)

    def items(self) -> Iterable[Tuple[K, V]]:
        for x in self:
            yield self._get_key(x), x

    def values(self) -> Iterable[V]:
        return iter(self)

    def __repr__(self) -> str:  # pragma: no cover - simple convenience
        cls = type(self).__name__
        return f"{cls}({list(self)!r})"


class VMapping[K, V](VMappingBase[K, V]):

    type Input = VMappingInput[str, V]
    _KEY_ATTR: ClassVar[str]

    @classmethod
    def has_key_attr(self) -> bool:
        """Return whether the class has a _KEY_ATTR defined."""
        return hasattr(self, "_KEY_ATTR")

    def _get_key(self, value: object) -> K:
        """Extract the key from a value using the class's _KEY_ATTR.

        Raises AttributeError with a clear message if the attribute is missing.
        """
        if not self.has_key_attr():
            raise AttributeError(
                f"Tried to add {type(value).__name__} to {self.__class__.__name__}, but it didn't have required attribute {self._KEY_ATTR!r}"
            )
        return getattr(value, self._KEY_ATTR)

    def __init_subclass__(cls, key_attr: str, **kwargs: Any) -> None:
        """Set the class-level key attribute name for subclasses.

        Usage:
            class ByName(VMapping, key_attr="name"):
                ...
        """
        super().__init_subclass__(**kwargs)
        cls._KEY_ATTR = key_attr

    def __init__(self, values: "VMappingInput[K, V]" = ()) -> None:
        # accept another VMapping or any iterable of values
        self._map = self._to_dict(values)

    # iteration yields values (not keys)
    def __iter__(self) -> Iterator[V]:
        return iter(self._map.values())

    def __len__(self) -> int:
        return len(self._map)

    # mapping-like access
    def __getitem__(self, key: K) -> V:
        return self._map[key]

    @abstractmethod
    def _with_values(self, values: Input) -> Self:
        pass

    def update(self, *others: "VMappingInput[K, V]") -> "VMapping[K, V]":
        """Return a new instance with keys from self and all provided others.

        Later arguments override earlier ones on key collisions.
        Operations are only allowed between exactly the same concrete class.
        """
        merged: dict[K, V] = dict(self._map)
        for other in others:
            asMapping = self._to_dict(other)
            # operations only allowed between exactly the same concrete class
            if type(other) is not type(self):
                raise TypeError(
                    f"Can only merge VMapping instances of the same concrete class: {type(self).__name__} != {type(other).__name__}"
                )
            merged.update(asMapping)

        # Construct a new instance of the same concrete class from merged values
        return self._with_values(merged.values())

    def to_mapping(self) -> Mapping[K, V]:
        """Expose the underlying plain mapping (read-only view)."""
        return dict(self._map)

    def __repr__(self) -> str:  # pragma: no cover - simple convenience
        cls = type(self).__name__
        return f"{cls}({list(self._map.values())!r})"


def deep_merge(a: Mapping, b: Mapping) -> dict:
    """
    Recursively merge two mappings.
    Values from *b* overwrite or merge into *a*.
    Returns a new dict; neither input is modified.
    """
    merged = dict(a)  # shallow copy of the left operand
    for key, b_val in b.items():
        a_val = merged.get(key)
        if isinstance(a_val, Mapping) and isinstance(b_val, Mapping):
            merged[key] = deep_merge(a_val, b_val)
        else:
            merged[key] = b_val
    return merged
