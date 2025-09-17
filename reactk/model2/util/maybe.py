from typing import overload
from expression import Option, Some, Nothing


def maybe_normalize[T](x: T | Option[T]) -> Option[T]:
    if x is Nothing:
        return Nothing
    if isinstance(x, Option):
        return x
    if x is None:
        return Nothing
    return Some(x)


type MaybeOption[T] = Option[T] | T
