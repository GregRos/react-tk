from abc import abstractmethod
from collections.abc import Iterable, Iterator, Mapping
from types import MethodType
from typing import Any, TypedDict, get_type_hints

from reactk.annotations.get_methods import get_attrs_downto


class AnnotationWrapper2:
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
            AnnotationWrapper2(x) for x in getattr(self._target, "__args__", [])
        )

    def metadata_of_type[X](self, *type: type[X]) -> Iterable["AnnotationWrapper2"]:
        for x in self.metadata:
            if isinstance(x, type):
                yield AnnotationWrapper2(x)

    @property
    def metadata(self):
        t = self
        match t.name:
            case "Annotated":
                for x in t.args[1:]:
                    yield from AnnotationWrapper2(x).metadata
            case "NotRequired" | "Unpack":
                yield from AnnotationWrapper2(t.args[0]).metadata
            case _ if not isinstance(t.target, type):
                yield t

    def _get_inner_type(self) -> type:
        t = self
        match t.name:
            case "Annotated" | "NotRequired" | "Unpack":
                return AnnotationWrapper2(t.args[0])._get_inner_type()
            case type() as t:
                return t
            case _:
                raise TypeError(f"Unknown annotation type {t.name!r}")

    @property
    def inner_type(self) -> type | None:
        """Return the inner / unwrapped type (inlined)."""
        x = self._get_inner_type()
        return x.value if x is not None else None


class KeyAccessor:

    @property
    @abstractmethod
    def key(self) -> str: ...
    def __init__(self, target: Any) -> None:
        self.target = target

    def set(self, value: Any) -> None:
        try:
            setattr(self.target, self.key, value)
        except Exception:
            pass

    @property
    def has_key(self) -> bool:
        return hasattr(self.target, self.key)

    def _get(self) -> Any:

        return getattr(self.target, self.key)

    def get(self) -> Any:
        return self._get()


class OrigAccessor(KeyAccessor):
    @property
    def key(self) -> str:
        return "__original__"

    def get(self) -> Any:
        if not self.has_key:
            return self.target
        cur = self
        while cur.has_key:
            cur = OrigAccessor(cur._get())
        return cur


class MethodReader:
    _annotations: dict[str, Any]
    _annotation_names: tuple[str, ...]

    def __init__(self, target: Any) -> None:
        orig_accessor = OrigAccessor(target)
        self.target = orig_accessor.get()
        self._refresh_annotations()

    def _refresh_annotations(self) -> None:
        self._annotations = get_type_hints(
            self.target, include_extras=True, localns={"Node": "object"}
        )
        self._annotation_names = tuple(
            x for x in self._annotations.keys() if x != "return"
        )

    def get_return(self) -> AnnotationWrapper2:
        try:
            return AnnotationWrapper2(self._annotations["return"])
        except KeyError:
            raise KeyError("return") from None

    def get_arg(self, pos: int | str) -> AnnotationWrapper2:
        if pos == "return":
            return self.get_return()
        try:
            if isinstance(pos, int):
                name = self._annotation_names[pos]
            else:
                name = pos
            return AnnotationWrapper2(self._annotations[name])
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
    def annotations(self) -> Mapping[str, AnnotationWrapper2]:
        return {k: self.get_annotation(k) for k in self._annotation_names}

    @property
    def methods(self) -> Iterable[str]:
        return self._methods.keys()

    def get_annotation(self, key: str) -> AnnotationWrapper2:
        try:
            return AnnotationWrapper2(self._annotations[key])
        except KeyError:
            raise KeyError(key) from None

    def get_method(self, key: str) -> MethodReader:
        try:
            return MethodReader(self._methods[key])
        except KeyError:
            raise KeyError(key) from None
