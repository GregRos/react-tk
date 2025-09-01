from typing import Any, Callable, Type, get_type_hints

from reactk.annotations.annotation_wrapper import AnnotationWrapper
from reactk.annotations.metadata_manager import MetadataManager


def get_metadata(t: Type) -> "MetadataManager":
    """Return a MetadataManager for the annotation's metadata."""
    return AnnotationWrapper(t).metadata


def get_metadata_of_type[X](target: Type, *metadata_type: type[X]) -> X | None:
    manager = get_metadata(target)
    return manager.of_types(*metadata_type)


def get_inner_type_value(ty: Type):
    return AnnotationWrapper(ty).inner_type


def get_props_type_from_callable(f: Callable):
    arg = next(
        x or v
        for k, v in get_type_hints(f, include_extras=True).items()
        if (x := get_inner_type_value(v))
    )
    return arg
