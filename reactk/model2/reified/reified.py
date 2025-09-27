from reactk.reflect.generic_reader import Reader_Generic
from reactk.reflect.reflector import Reflector

reflector = Reflector()


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
        sig = reflector.generic(cls)

        if not sig:
            args = ()
        elif sig.is_all_bound:
            args = tuple(r.value for r in sig)  # type: ignore[attr-defined]
        else:
            raise TypeError(
                f"{cls.__name__} must be parameterized before instantiation"
            )

        obj = super().__call__(*a, **kw)
        obj.__args__ = args
        return obj
