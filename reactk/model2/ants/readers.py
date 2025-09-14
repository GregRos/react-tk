from collections.abc import Iterable, Mapping
from ctypes import Union
from dataclasses import dataclass, field
from types import MethodType, UnionType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    Literal,
    TypedDict,
    get_origin,
    get_type_hints,
)


from reactk.model2.ants.args_accessor import MetadataAccessor, UnderscoreNameAccessor
from reactk.model2.ants.base import Reader_Base
from reactk.model2.util.core_reflection import get_attrs_downto
from reactk.model2.ants.key_accessor import KeyAccessor
from reactk.model2.util.str import format_signature
from reactk.model2.util.type_hints import get_type_hints_up_to

if TYPE_CHECKING:
    from reactk.model2.ants.generic_reader import SomeTypeVarReader, Reader_Generic


@dataclass(eq=True, unsafe_hash=True)
class Reader_Annotation(Reader_Base):
    """Wrap an annotation object and expose convenience getters.

    This class contains the implementations of the commonly used
    annotation helper functions so callers can either use the
    module-level wrappers (kept for backward compatibility) or call
    these methods directly from the class.
    """

    @property
    def generic(self) -> "Reader_Generic":
        return self.reflector.generic(self.target)

    @property
    def is_required(self) -> bool:
        t = self
        match t.name:
            case "NotRequired":
                return False
            case "Optional":
                return True
            case "Annotated" | "Unpack":
                var = t.generic[0]
                # local import to avoid import-time cycles when generic_reader imports readers
                from reactk.model2.ants.generic_reader import is_not_bound

                if is_not_bound(var):
                    raise TypeError("First generic argument is not a bound TypeVar")
                return var.value.is_required
            case _:
                return True

    @property
    def name(self) -> str:
        t = self.target
        origin = self.generic.origin
        if origin:
            return origin.name
        elif _name := UnderscoreNameAccessor(self.target):
            return _name.get(t)
        elif isinstance(t, type):
            return t.__name__
        else:
            assert False, f"Unknown annotation type: {t!r}"

    def __str__(self) -> str:
        return str(self.target)

    def metadata_of_type[X](self, *type: type[X]) -> Iterable["Reader_Annotation"]:
        for x in self.metadata:
            if isinstance(x, type):
                yield self.reflector.annotation(x)

    @property
    def metadata(self):

        t = self
        match t.name:
            case "Annotated":
                yield from self.access(MetadataAccessor).get(())
            case "NotRequired" | "Unpack":
                yield from self.reflector.annotation(t.generic[0].value).metadata

    def _get_inner_type(self) -> Any:
        t = self
        if t.name in ("Annotated", "NotRequired", "Unpack", "Required", "Optional"):
            return t.generic[0].value._get_inner_type()
        return t.target

    def __eq__(self, other: object) -> bool:
        return type(other) == type(self) and self.target == other.target

    @property
    def inner_type(self) -> Any:
        """Return the inner / unwrapped type (inlined)."""
        x = self._get_inner_type()
        return x

    @property
    def inner_class(self) -> "Reader_Class":
        """Return a ClassReader for the inner type, if it's a class."""
        t = self.inner_type

        if not isinstance(t, type):
            if o := self.generic.origin:
                t = o.target
            if not isinstance(t, type):
                raise TypeError(f"Inner type {t!r} is not a class")

        return self.reflector.type(t)


class OrigAccessor(KeyAccessor[Callable[..., Any]]):
    @property
    def key(self) -> str:
        return "__reactk_original__"


@dataclass(eq=True, unsafe_hash=True, repr=False)
class Reader_Method(Reader_Base):
    _annotations: dict[str, Any] = field(init=False)
    _annotation_names: tuple[str, ...] = field(init=False)

    def __post_init__(self) -> None:
        target = self.target
        orig_accessor = OrigAccessor(target)
        self.target = orig_accessor.get(target)
        self._refresh_annotations()

    @property
    def name(self) -> str:
        return self.target.__name__

    def _refresh_annotations(self) -> None:
        self._annotations = get_type_hints(
            self.target, include_extras=True, localns={"Node": "object"}
        )
        self._annotation_names = tuple(
            x for x in self._annotations.keys() if x != "return"
        )

    def returns(self) -> Reader_Annotation:
        try:
            return self.reflector.annotation(self._annotations["return"])
        except KeyError:
            raise KeyError("return") from None

    @property
    def _debug_signature(self) -> str:
        return format_signature(self.target)

    def __str__(self) -> str:
        return f"【 MethodReader: {self._debug_signature} 】"

    def arg(self, pos: int | str) -> Reader_Annotation:
        if pos == "return":
            return self.returns()
        if isinstance(pos, int):
            name = self._annotation_names[pos]
        else:
            name = pos
        return self.reflector.annotation(self._annotations[name])


@dataclass(eq=True, unsafe_hash=True, repr=False)
class Reader_Class(Reader_Base):
    _annotations: dict[str, Any] = field(init=False)
    _methods: dict[str, Any] = field(init=False)
    _annotation_names: tuple[str, ...] = field(init=False)

    def __post_init__(self) -> None:
        target = self.target
        if not issubclass(target, object):
            raise ValueError("Target must be a class")
        if issubclass(target, MethodType):
            raise ValueError("Target cannot be a method")
        self._refresh_annotations()

    @property
    def name(self) -> str:
        return self.target.__name__

    def _refresh_annotations(self) -> None:
        self._annotations = self.reflector.get_type_hints(self.target)
        self._annotation_names = tuple(self._annotations.keys())
        attrs = get_attrs_downto(self.target, {object, Mapping, TypedDict})
        self._methods = {k: v for k, v in attrs.items() if callable(v)}

    @property
    def annotations(self) -> Mapping[str, Reader_Annotation]:
        return {k: self.annotation(k) for k in self._annotation_names}

    @property
    def methods(self) -> Mapping[str, Reader_Method]:
        return self._methods

    def annotation(self, key: str) -> Reader_Annotation:
        return self.reflector.annotation(self._annotations[key])

    def method(self, key: str) -> Reader_Method:
        return self.reflector.method(self._methods[key])
