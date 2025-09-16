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


def type_arg(
    name: str,
    /,
    *,
    value: Any,
    lower_bound: Any = None,
    default: Any = None,
    is_defaulted: bool = False,
):
    return r.type_arg(
        TypeVar(name, bound=lower_bound, default=default),  # type: ignore
        value=value,
        is_defaulted=is_defaulted,
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


class Generic_Bad[A, B]:
    pass


@pytest.mark.parametrize(
    "got,expected",
    (
        (int, []),
        (list[int], special_type_args(int)),
        (dict[str, int], special_type_args(str, int)),
        (list, ()),
        (dict, ()),
        (NotRequired[int], special_type_args(int)),
        (Unpack[dict[str, int]], special_type_args(dict[str, int])),
        (G_1, (type_var("A"),)),
        (G_2, (type_var("A"), type_var("B"))),
        (G_1_Lower, (type_var("A", bound=int),)),
        (G_1[int], (type_arg("A", value=int),)),
        (G_2[int, str], (type_arg("A", value=int), type_arg("B", value=str))),
        (G_1_Lower[int], (type_arg("A", value=int, lower_bound=int),)),
        (
            G_1_Lower_Default[str],
            (type_arg("A", value=str, lower_bound=object, default=str),),
        ),
        (
            G_1_Lower_Default,
            (
                type_arg(
                    "A", value=str, lower_bound=object, default=str, is_defaulted=True
                ),
            ),
        ),
    ),
)
def it_validates_generic_signature(got, expected):
    for idx, (g, e) in enumerate(zip_longest(r._get_generic_signature(got), expected)):
        assert g == e or g.is_similar_to(e), f"mismatch at index {idx}: {g} != {e}"


@pytest.mark.parametrize(
    "got,index,expected",
    (
        # list[int] by numeric index and by name
        (list[int], 0, special_type_args(int)[0]),
        # dict[str, int] second type argument by index
        (dict[str, int], 1, special_type_args(str, int)[1]),
        # generic classes by type-var name
        (G_1[int], "A", type_arg("A", value=int)),
        (G_2[int, str], "B", type_arg("B", value=str)),
        # lower bound / default cases
        (G_1_Lower[int], 0, type_arg("A", value=int, lower_bound=int)),
        (
            G_1_Lower_Default[str],
            0,
            type_arg("A", value=str, lower_bound=object, default=str),
        ),
        (
            G_1_Lower_Default,
            0,
            type_arg(
                "A", value=str, lower_bound=object, default=str, is_defaulted=True
            ),
        ),
    ),
)
def it_gets_type_var_by_index(got, index, expected):
    assert r.annotation(got).generic[index].is_similar_to(expected)


@pytest.mark.parametrize(
    "target,expected",
    (
        (G_1[int], 1),
        (G_1, 1),
        (G_2[int, str], 2),
        (G_2, 2),
        (list, 0),
        (int, 0),
    ),
)
def it_gets_number_of_type_vars(target, expected):
    assert len(r.annotation(target).generic) == expected


@pytest.mark.parametrize(
    "target,key,expected",
    (
        (G_1[int], "A", True),
        (G_1, "A", True),
        (G_1, 0, True),
        (G_1, "B", False),
        (G_2[int, str], "B", True),
        (G_2, "B", True),
        (list, 0, False),
    ),
)
def it_gets_key_in_generic(target, key, expected):
    assert (key in r.annotation(target).generic) == expected
