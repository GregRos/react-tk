from typing import Type


def get_annotation_name(t: Type):
    if getattr(t, "_name", None):
        return t._name
    origin = getattr(t, "__origin__", None)
    if origin is not None:
        return origin.__name__
    return None
