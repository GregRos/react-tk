from abc import ABC
from reactk.model2.ants.args_accessor import ArgsAccessor, TypeParamsAccessor
from collections.abc import Iterable, Iterator
from reactk.model2.ants.readers import AnnotationReader, ClassReader


from typing import Any, ClassVar, Literal, TypeVar, get_origin


class _Base_Reader_TypeVar(ABC):

    def __init__(self, target: TypeVar) -> None:
        if not isinstance(target, TypeVar):
            raise TypeError(f"Target {target!r} is not a TypeVar")
        self.target = target

    @property
    def name(self) -> str:
        return self.target.__name__

    @property
    def bound(self) -> AnnotationReader | None:
        if self.target.__bound__ is None:
            return None
        return AnnotationReader(self.target.__bound__)

    @property
    def constraints(self) -> tuple[AnnotationReader, ...]:
        return tuple(AnnotationReader(x) for x in self.target.__constraints__)

    @property
    def default(self) -> AnnotationReader | None:
        if self.target.__default__ is None:
            return None
        return AnnotationReader(self.target.__default__)

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
    is_bound: Literal[False] = False


class Reader_BoundTypeVar(_Base_Reader_TypeVar):
    is_bound: Literal[True] = True

    def __init__(self, target: TypeVar, bound_value: Any) -> None:
        super().__init__(target)
        self.value = bound_value

    def __str__(self) -> str:
        # Format: {Name}={BoundValue}
        name = self.name
        parts = [name]
        parts.append(f"={str(self.value)}")
        return "".join(parts)


# Union type for readers that may be bound or unbound
SomeTypeVarReader = Reader_TypeVar | Reader_BoundTypeVar


class Reader_Generic(Iterable[SomeTypeVarReader]):
    """Read the generic signature for a class or a parameterized generic alias.

    This reader will produce either `TypeVarReader` (unbound) or
    `BoundTypeVarReader` (bound) for each declared type-variable on the
    origin. It accepts either a plain class (no args) or a parameterized
    alias; use :attr:`is_all_bound` to check whether every type-var has a
    bound value (from args or defaults).
    """

    def __init__(self, target: Any) -> None:
        # Determine origin and args (if any)
        origin = get_origin(target)
        if origin is None:
            if not isinstance(target, type):
                raise TypeError(f"Target {target!r} is not a class or generic alias")
            origin = target

        self.target = origin
        # declared type parameters on the origin
        params = TypeParamsAccessor(origin).get(())

        # runtime args on the supplied target (may be absent)
        ta = ArgsAccessor(target)
        args: tuple = ()
        if ta.has_key:
            args = ta.get(())

        readers: list[SomeTypeVarReader] = []
        for idx, param in enumerate(params):
            param_reader = _Base_Reader_TypeVar(param)
            param_default = param_reader.default
            # supplied arg wins
            if idx < len(args) and args[idx] is not None:
                readers.append(Reader_BoundTypeVar(param, args[idx]))
            # fallback to TypeVar default if present
            elif param_default is not None:
                readers.append(Reader_BoundTypeVar(param, param_default.target))
            else:
                readers.append(Reader_TypeVar(param))

        self._readers = readers
        self._by_name = {r.name: r for r in self._readers}

    def __bool__(self) -> bool:
        """Truthiness indicates whether this signature contains any type vars."""
        return bool(self._readers)

    def __len__(self) -> int:
        return len(self._readers)

    def __iter__(self) -> Iterator[SomeTypeVarReader]:
        return iter(self._readers)

    @property
    def cls(self):
        return ClassReader(self.target)

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
        return ClassReader(self.target)

    def __str__(self) -> str:
        return f"{self.root.name}[{', '.join(str(r) for r in self._readers)}]"

    @property
    def is_all_bound(self) -> bool:
        return all(isinstance(r, Reader_BoundTypeVar) for r in self._readers)
