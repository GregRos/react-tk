from collections.abc import Iterable
from typing import Any, Type

from reactk.annotations.metadata_manager import MetadataManager


class AnnotationWrapper[T]:
    """Wrap an annotation object and expose convenience getters.

    This class contains the implementations of the commonly used
    annotation helper functions so callers can either use the
    module-level wrappers (kept for backward compatibility) or call
    these methods directly from the class.
    """

    def __init__(self, annotation: T) -> None:
        self._annotation = annotation

    @property
    def value(self) -> T:
        return self._annotation

    @property
    def kids(self) -> tuple["AnnotationWrapper", ...]:
        return self.args

    # ---- Getters -------------------------------------------------
    @property
    def name(self) -> str | None:
        """Return the annotation's base name (e.g. 'Annotated', or None).

        Implementation inlined to operate on this instance's annotation.
        """
        t = self._annotation
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
            AnnotationWrapper(x) for x in getattr(self._annotation, "__args__", [])
        )

    def metadata_of_type[X](self, type: type[X]) -> Iterable["AnnotationWrapper[X]"]:
        for x in self.metadata:
            if isinstance(x, type):
                yield AnnotationWrapper[X](x)

    @property
    def metadata(self):
        t = self
        match t.name:
            case "Annotated":
                for x in t.args[1:]:
                    yield from AnnotationWrapper(x).metadata
            case "NotRequired" | "Unpack":
                yield from AnnotationWrapper(t.args[0]).metadata
            case _:
                yield t

    def _get_inner_type(self) -> "type | None":
        t = self
        match t.name:
            case "Annotated" | "NotRequired" | "Unpack":
                return AnnotationWrapper(t.args[0])._get_inner_type()
            case _:
                return t  # type: ignore

    @property
    def inner_type(self) -> type | None:
        """Return the inner / unwrapped type (inlined)."""
        x = self._get_inner_type()
        return x.value if x is not None else None
