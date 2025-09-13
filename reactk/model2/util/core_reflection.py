from inspect import isfunction


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


def get_mro_up_to(cls: type, top: type | None = None) -> list[type]:
    """Return the MRO slice for cls up to top (inclusive).

    If top is None or not in cls.__mro__, returns [cls].
    """
    if top is None:
        return [cls]
    mro = list(cls.__mro__)
    if top in mro:
        stop_index = mro.index(top) + 1
        return mro[:stop_index]
    return [cls]
