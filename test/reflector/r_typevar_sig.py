"""
test
"""

from itertools import zip_longest
from typing import Any, NotRequired, TypeVar, Unpack

import pytest
from reactk.model2.ants.reflector import Reflector


r = Reflector()


def type_var(name: str, /, *, bound: Any = None, default: Any = None):
    return r.type_var(TypeVar(name, bound=bound, default=default))  # type: ignore


def type_arg(name: str, /, *, value: Any, lower_bound: Any = None, default: Any = None):
    return r.type_arg(
        TypeVar(name, bound=lower_bound, default=default), value=value  # type: ignore
    )


def special_type_args(*values: Any):
    return tuple(
        r.type_arg(TypeVar(f"_{pos}"), value=value, is_undeclared=True)
        for pos, value in enumerate(values)
    )


class G_1[A]:
    pass


class G_2[A, B]:
    pass


class G_1_Lower[A: int]:
    pass


class G_1_Lower_Default[A: object = str]:
    pass


@pytest.mark.parametrize(
    "got,expected",
    (
        (int, []),
        (list[int], special_type_args(int)),
        (dict[str, int], special_type_args(str, int)),
        (NotRequired[int], special_type_args(int)),
        (Unpack[dict[str, int]], special_type_args(dict[str, int])),
        (G_1[int], (type_arg("A", value=int),)),
        (G_2[int, str], (type_arg("A", value=int), type_arg("B", value=str))),
        (G_1_Lower[int], (type_arg("A", value=int, lower_bound=int),)),
        (
            G_1_Lower_Default[str],
            (type_arg("A", value=str, lower_bound=int, default=str),),
        ),
    ),
)
def it_validates_generic_signature(got, expected):
    for idx, (g, e) in enumerate(zip_longest(r._get_generic_signature(got), expected)):
        assert g == e or g.is_similar(e), f"mismatch at index {idx}: {g} != {e}"
