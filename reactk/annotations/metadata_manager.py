from typing import Annotated, Any, Iterable, Tuple, Type, TypeVar

from reactk.annotations.annotation_wrapper import AnnotationWrapper
from reactk.model.annotation_reader import AnnotationReader

X = TypeVar("X")


def unpack_metadata(*ts: AnnotationWrapper) -> Iterable[Any]:
    """Return the metadata tuple from an Annotated type, or an empty tuple."""
    for wrapper in ts:
        if wrapper.name == "Annotated":
            for x in wrapper.args[1:]:
                yield from unpack_metadata(x)
        else:
            yield wrapper.value


class MetadataManager:
    """Manage a tuple of metadata objects (the __metadata__ from Annotated).

    Provides utility methods to query the metadata by type.
    """

    def __init__(self, *roots: AnnotationWrapper) -> None:
        self._roots = roots

    @property
    def metadata(self) -> Iterable[Any]:
        return unpack_metadata(*self._roots)

    def of_types(self, *metadata_type: type[X]) -> X | None:
        """Return the first metadata entry that is an instance of any provided types.

        Mirrors the behaviour of the former `get_metadata_of_type` function.
        """
        return next(
            (x for x in self.metadata if isinstance(x, metadata_type)),
            None,
        )
