from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from reactk.model2.ants.args_accessor import ArgsAccessor, TypeParamsAccessor
from collections.abc import Iterable, Iterator
from reactk.model2.ants.base import Reader_Base
from itertools import zip_longest


from typing import TYPE_CHECKING, Any, Literal, TypeIs, TypeVar

# Import readers at module load time. `readers.py` only imports
# from `generic_reader` under TYPE_CHECKING or lazily, so this
# does not create a circular import at runtime.
if TYPE_CHECKING:
    from reactk.model2.ants.readers import Reader_Annotation, Reader_Class
    from reactk.model2.ants.reflector import Reflector


@dataclass
class _Base_Reader_TypeVar(Reader_Base, ABC):
    target: TypeVar
    reflector: "Reflector"
    is_undeclared: bool = field(default=False, kw_only=True)

    @property
    @abstractmethod
    def is_bound(self) -> bool: ...

    @property
    def name(self) -> str:
        return self.target.__name__

    @property
    def bound(self) -> Reader_Annotation | None:
        if self.target.__bound__ is None:
            return None
        return self.reflector.annotation(self.target.__bound__)

    @property
    def constraints(self) -> tuple[Reader_Annotation, ...]:
        return tuple(self.reflector.annotation(x) for x in self.target.__constraints__)

    @property
    def default(self) -> Reader_Annotation | None:
        if self.target.__default__ is None:
            return None
        return self.reflector.annotation(self.target.__default__)

    def __str__(self) -> str:
        # Format: {Name}: {Bound.Name} = {Default.Name}
        name = self.name
        parts = [name]
        b = self.bound
        if b is not None:
            parts.append(f": {str(b)}")

        d = self.default
        if d is not None:
            parts.append(f" = {str(d)}")
        return "".join(parts)


class Reader_TypeVar(_Base_Reader_TypeVar):
    @property
    def is_bound(self) -> Literal[True]:
        return True

    @property
    def value(self) -> Reader_Annotation:
        raise TypeError(f"TypeVar {self} is not bound to a value")


@dataclass
class Reader_BoundTypeVar(_Base_Reader_TypeVar):
    value: Reader_Annotation

    @property
    def is_bound(self) -> Literal[True]:
        return True

    def __eq__(self, other: object) -> bool:
        return (
            type(other) == type(self)
            and self.target == other.target
            and self.value == other.value
        )

    def __hash__(self) -> int:
        return hash((self.target, self.value))

    def __str__(self) -> str:
        # Format: {Name}={BoundValue}
        name = self.name
        parts = [name]
        parts.append(f"={str(self.value)}")
        return "".join(parts)


# Union type for readers that may be bound or unbound
SomeTypeVarReader = Reader_TypeVar | Reader_BoundTypeVar


def _build_readers_for_origin_and_target(
    target: Any, reflector: "Reflector"
) -> list[SomeTypeVarReader]:
    # declared type parameters on the origin
    params = TypeParamsAccessor(target).get(())
    # runtime args on the supplied target (may be absent)
    ta = ArgsAccessor(target)
    args: tuple = ()
    if ta.has_key:
        args = ta.get(())

    readers: list[SomeTypeVarReader] = []
    for idx, (param, arg) in enumerate(zip_longest(params, args, fillvalue=None)):
        if param is None:
            param_reader = reflector.type_var(TypeVar(f"_{idx}"), is_undeclared=True)
        else:
            param_reader = reflector.type_var(param)

        # normal handling when a declared type-variable exists
        param_default = param_reader.default

        # supplied arg wins
        if arg is not None:
            readers.append(
                reflector.type_arg(
                    param_reader.target, arg, is_undeclared=param_reader.is_undeclared
                )
            )
        # fallback to TypeVar default if present
        elif param_default is not None:
            readers.append(
                reflector.type_arg(
                    param_reader.target,
                    param_default.target,
                    is_undeclared=param_reader.is_undeclared,
                )
            )
        else:
            # param_reader is already an unbound TypeVar reader
            readers.append(param_reader)

    return readers


@dataclass
class Reader_Generic(Reader_Base, Iterable[SomeTypeVarReader]):
    """Read the generic signature for a class or a parameterized generic alias.

    This reader will produce either `TypeVarReader` (unbound) or
    `BoundTypeVarReader` (bound) for each declared type-variable on the
    origin. It accepts either a plain class (no args) or a parameterized
    alias; use :attr:`is_all_bound` to check whether every type-var has a
    bound value (from args or defaults).
    """

    def __post_init__(self) -> None:
        target = self.target
        # replace the in-place reader construction with the helper call
        self._readers = _build_readers_for_origin_and_target(target, self.reflector)
        self._by_name = {r.name: r for r in self._readers}

    def __bool__(self) -> bool:
        """Truthiness indicates whether this signature contains any type vars."""
        return bool(self._readers)

    def __len__(self) -> int:
        return len(self._readers)

    def __iter__(self) -> Iterator[SomeTypeVarReader]:
        return iter(self._readers)

    def __getitem__(self, key: int | str) -> SomeTypeVarReader:
        """Index by integer position or by type-var name."""
        match key:
            case int():
                return self._readers[key]
            case str():
                return self._by_name[key]
        raise KeyError(key) from None

    @property
    def root(self):
        reader = self.reflector.annotation(self.target)
        return reader.origin or reader

    def __str__(self) -> str:
        return f"{self.root.name}[{', '.join(str(r) for r in self._readers)}]"

    @property
    def is_all_bound(self) -> bool:
        return all(isinstance(r, Reader_BoundTypeVar) for r in self._readers)


def is_bound(tv: _Base_Reader_TypeVar) -> TypeIs[Reader_BoundTypeVar]:
    return isinstance(tv, Reader_BoundTypeVar)


def is_not_bound(tv: _Base_Reader_TypeVar) -> TypeIs[Reader_TypeVar]:
    return isinstance(tv, Reader_TypeVar)
