from reactk.model2.ants.generic_reader import Reader_Generic


class ParametricMeta(type):
    def __getitem__(cls, args):
        if not isinstance(args, tuple):
            args = (args,)
        name = (
            f"{cls.__name__}[{', '.join(getattr(a,'__name__',repr(a)) for a in args)}]"
        )
        return type(name, (cls,), {"__origin__": cls, "__args__": args})

    def __call__(cls, *a, **kw):
        # If this is a specialized subclass, it already has __args__
        args = getattr(cls, "__args__", None)
        if args is None:
            # Use Reader_Generic to inspect declared type params and defaults.
            # Do not catch construction errors here — let them propagate.
            sig = Reader_Generic(cls)

            # If there are no type params, treat as normal class (no args)
            if not sig:
                args = ()
            else:
                # If all typevars already have defaults/args, we can use them
                if sig.is_all_bound:
                    # gather bound values in order
                    args = tuple(r.value for r in sig)  # type: ignore[attr-defined]
                else:
                    raise TypeError(
                        f"{cls.__name__} must be parameterized before instantiation"
                    )

        obj = super().__call__(*a, **kw)
        obj.__args__ = args
        return obj


# Python 3.13+ syntax with defaults:
class X[T = int](metaclass=ParametricMeta):  # default T is int
    pass


a = X()  # uses default -> (int,)
b = X[str]()  # explicit override -> (str,)
assert getattr(a, "__args__") == (int,)
assert getattr(b, "__args__") == (str,)
