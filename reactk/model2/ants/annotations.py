from collections.abc import Iterable, Iterator, Mapping
from types import MethodType
from typing import TYPE_CHECKING, Any, Callable, TypedDict, get_type_hints

from reactk.model2.ants.get_methods import get_attrs_downto
from reactk.model2.ants.key_accessor import KeyAccessor

if TYPE_CHECKING:
    from reactk.model2.prop_ants.c_meta import some_meta


class AnnotationWrapper:
    """Wrap an annotation object and expose convenience getters.

    This class contains the implementations of the commonly used
    annotation helper functions so callers can either use the
    module-level wrappers (kept for backward compatibility) or call
    these methods directly from the class.
    """

    def __init__(self, target: Any) -> None:
        self._target = target

    @property
    def target(self) -> Any:
        return self._target

    @property
    def is_required(self) -> bool:
        t = self
        match t.name:
            case "NotRequired":
                return False
            case "Optional":
                return True
            case "Annotated" | "Unpack":
                return AnnotationWrapper(t.args[0]).is_required
            case _:
                return True

    # ---- Getters -------------------------------------------------
    @property
    def name(self) -> str | None:
        """Return the annotation's base name (e.g. 'Annotated', or None).

        Implementation inlined to operate on this instance's annotation.
        """
        t = self._target
        if name := getattr(t, "_name", None):
            return name
        origin = getattr(t, "__origin__", None)
        if origin is not None:
            return origin.__name__
        return None

    @property
    def args(self) -> tuple[Any, ...]:
        """Return the annotation's __args__ tuple, or None."""
        return tuple(
            AnnotationWrapper(x) for x in getattr(self._target, "__args__", [])
        )

    def metadata_of_type[X](self, *type: type[X]) -> Iterable["AnnotationWrapper"]:
        for x in self.metadata:
            if isinstance(x, type):
                yield AnnotationWrapper(x)

    @property
    def metadata(self):
        t = self
        match t.name:
            case "Annotated":
                for x in t.args[1:]:
                    yield from AnnotationWrapper(x).metadata
            case "NotRequired" | "Unpack":
                yield from AnnotationWrapper(t.args[0]).metadata
            case _ if not isinstance(t.target, type):
                yield t

    def _get_inner_type(self) -> type:
        t = self
        match t.name:
            case "Annotated" | "NotRequired" | "Unpack":
                return AnnotationWrapper(t.args[0])._get_inner_type()
            case type() as t:
                return t
            case _:
                raise TypeError(f"Unknown annotation type {t.name!r}")

    @property
    def inner_type(self) -> type:
        """Return the inner / unwrapped type (inlined)."""
        x = self._get_inner_type()
        return x.value

    @property
    def inner_type_reader(self) -> "ClassReader":
        """Return a ClassReader for the inner type, if it's a class."""
        t = self.inner_type
        if t is None or not isinstance(t, type):
            raise TypeError(f"Inner type {t!r} is not a class")
        return ClassReader(t)


class OrigAccessor(KeyAccessor[Callable[..., Any]]):
    @property
    def key(self) -> str:
        return "__reactk_original__"

    def get(self) -> "OrigAccessor.Value":
        if not self.has_key:
            return self.target
        cur = self
        while cur.has_key:
            cur = OrigAccessor(cur._get())
        return cur.target


class MethodReader:
    _annotations: dict[str, Any]
    _annotation_names: tuple[str, ...]

    def __init__(self, target: Any) -> None:
        orig_accessor = OrigAccessor(target)
        self.target = orig_accessor.get()
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

    def get_return(self) -> AnnotationWrapper:
        try:
            return AnnotationWrapper(self._annotations["return"])
        except KeyError:
            raise KeyError("return") from None

    def __getitem__[X](self, accessor: type[KeyAccessor[X]]) -> X | None:
        ma = accessor(self.target)
        return ma.get() if ma.has_key else None

    def __setitem__[X](self, accessor: type[KeyAccessor[X]], value: X) -> None:
        ma = accessor(self.target)
        ma.set(value)

    def get_arg(self, pos: int | str) -> AnnotationWrapper:
        if pos == "return":
            return self.get_return()
        try:
            if isinstance(pos, int):
                name = self._annotation_names[pos]
            else:
                name = pos
            return AnnotationWrapper(self._annotations[name])
        except (IndexError, KeyError):
            raise KeyError(pos) from None


class ClassReader:
    _annotations: dict[str, Any]
    _methods: dict[str, Any]
    _annotation_names: tuple[str, ...]

    def __init__(self, target: type) -> None:
        if not issubclass(target, object):
            raise ValueError("Target must be a class")
        if issubclass(target, MethodType):
            raise ValueError("Target cannot be a method")
        self.target = target

    def _refresh_annotations(self) -> None:
        self._annotations = get_type_hints(
            self.target, include_extras=True, localns={"Node": "object"}
        )
        self._annotation_names = tuple(self._annotations.keys())
        attrs = get_attrs_downto(self.target, {object, Mapping, TypedDict})
        self._methods = {k: v for k, v in attrs.items() if callable(v)}

    @property
    def annotations(self) -> Mapping[str, AnnotationWrapper]:
        return {k: self.get_annotation(k) for k in self._annotation_names}

    @property
    def methods(self) -> Mapping[str, MethodReader]:
        return self._methods

    def get_annotation(self, key: str) -> AnnotationWrapper:
        try:
            return AnnotationWrapper(self._annotations[key])
        except KeyError:
            raise KeyError(key) from None

    def get_method(self, key: str) -> MethodReader:
        try:
            return MethodReader(self._methods[key])
        except KeyError:
            raise KeyError(key) from None
