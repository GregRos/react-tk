from typing import Any, Callable, Type, get_type_hints

from reactk.annotations.get_annotation_name import get_annotation_name


def get_metadata(t: Type) -> tuple[Any, ...]:
    origin = get_annotation_name(t)
    if origin == "Annotated":
        return t.__metadata__  # type: tuple[Type, ...]
    else:
        return ()  # type: tuple[Type, ...]


def get_metadata_of_type[X](target: Type, *metadata_type: type[X]) -> X | None:
    metadata = get_metadata(target)
    return next(
        (x for x in metadata if any(isinstance(x, t) for t in metadata_type)), None
    )


def get_inner_type_value(ty: Type):
    t = ty
    while t is not None:
        annotation_name = get_annotation_name(t)
        if annotation_name in ("Annotated", "NotRequired", "Unpack"):
            t = t.__args__[0]  # type: Type
        else:
            return t


def get_props_type_from_callable(f: Callable):
    arg = next(
        x or v
        for k, v in get_type_hints(f, include_extras=True).items()
        if (x := get_inner_type_value(v))
    )
    return arg
