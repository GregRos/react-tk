from inspect import isfunction
from typing import Any

from expression import Nothing, Option
from funcy import first, takewhile


def get_attrs_downto(cls, stop_at: set[type]):
    def iter_attrs(cls):
        for attr_name in vars(cls):
            attr = getattr(cls, attr_name)
            yield attr_name, attr

        for base_class in cls.__mro__[1:]:
            if base_class in stop_at:
                break
            yield from iter_attrs(base_class)

    result = {}
    for name, method in iter_attrs(cls):
        if name not in result:
            result[name] = method

    return result


type type_reference = type | str


def is_match_ref(tr: type_reference):
    def _is_match_ref(t: type) -> bool:
        if isinstance(tr, str):
            return t.__name__ == tr
        return t is tr

    return _is_match_ref


def none_match_ref(*trs: type_reference):
    matchers = [is_match_ref(tr) for tr in trs]

    def _all_match_ref(t: type) -> bool:
        return all(not matcher(t) for matcher in matchers)

    return _all_match_ref


def get_mro_up_to(
    cls: type, top: type_reference | tuple[type_reference, ...]
) -> list[type]:
    """Return the MRO slice for cls up to top (inclusive).

    If top is None or not in cls.__mro__, returns [cls].
    """
    top = (top,) if isinstance(top, type) else top
    if top is None:
        return [cls]
    mro = list(cls.__mro__)
    return [*takewhile(none_match_ref(*top), mro)]


def has_attr_skip_hook(obj: object, name: str) -> bool:
    """Check if obj has attribute name, ignoring __getattr__ and __getattribute__."""
    attr = get_attr_skip_hook(obj, name)
    if attr is not Nothing:
        return True

    annotations = get_attr_skip_hook(obj, "__annotations__")
    if annotations is not Nothing and name in annotations:
        return True
    return False


def get_attr_skip_hook(obj: object, name: str) -> Option[Any]:
    """Check if obj has attribute name, ignoring __getattr__ and __getattribute__."""
    if own := obj.__dict__.get(name):
        return own
    if inherited := getattr(type(obj), name, None):
        return inherited

    return Nothing
