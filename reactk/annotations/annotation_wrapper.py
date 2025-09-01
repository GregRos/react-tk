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
    def metadata(self) -> MetadataManager:
        """Return a MetadataManager wrapping the Annotated's metadata tuple."""
        origin = self.name
        return MetadataManager(self)

    @property
    def args(self) -> tuple[Any, ...]:
        """Return the annotation's __args__ tuple, or None."""
        return tuple(
            AnnotationWrapper(x) for x in getattr(self._annotation, "__args__", [])
        )

    def _get_inner_type(self) -> "AnnotationWrapper | None":
        t = self
        while t is not None:
            if t.name in ("Annotated", "NotRequired", "Unpack"):
                t = t.args[0]  # type: ignore[attr-defined]
            else:
                return t
        return None

    @property
    def has_inner_type(self) -> bool:
        """Return whether the annotation has an inner / unwrapped type."""
        return self._get_inner_type() is not None

    @property
    def inner_type(self) -> type | None:
        """Return the inner / unwrapped type (inlined)."""
        x = self._get_inner_type()
        return x.value if x is not None else None
