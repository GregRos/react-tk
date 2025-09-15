from typing import Annotated, Unpack, NotRequired, Required, Union
import pytest

from reactk.model2.ants.reflector import Reflector

# module-level reflector instance used by all tests
r: Reflector = Reflector()


# Move nested example classes to module scope
class Example:
    pass


class Example_A[A]:
    pass


@pytest.mark.parametrize(
    "target,expected",
    [
        (int, int),
        (list[int], list[int]),
        (dict[str, int], dict[str, int]),
        (Annotated[int, "meta"], int),
        (Unpack[dict[str, int]], dict[str, int]),
        (NotRequired[int], int),
        (Annotated[Unpack[dict[str, int]], "meta"], dict[str, int]),
        (Required[int], int),
        (Annotated[NotRequired[int], "meta"], int),
    ],
)
def it_has_right_inner_type(target, expected):
    ann = r.annotation(target)
    assert ann.inner_type == expected


@pytest.mark.parametrize(
    "target,expected",
    [
        (int, "int"),
        (list[int], "list"),
        (dict[str, int], "dict"),
        (Annotated[int, "meta"], "Annotated"),
        (Unpack[dict[str, int]], "Unpack"),
        (NotRequired[int], "NotRequired"),
        (Union[int, str], "Union"),
    ],
)
def it_has_right_name(target, expected):
    ann = r.annotation(target)
    assert ann.name == expected


@pytest.mark.parametrize(
    "target,expected",
    [
        (int, int),
        (list[int], list),
        (dict[str, int], dict),
    ],
)
def it_has_correct_inner_class(target, expected):
    ann = r.annotation(target)
    assert ann.inner_class == r.type(expected)


@pytest.mark.parametrize(
    "target,expected",
    [
        (int, ()),
        (list[int], ()),
        (Annotated[int, "meta"], ("meta",)),
        (Annotated[list[int], "meta1", "meta2"], ("meta1", "meta2")),
        (Annotated[NotRequired[int], "meta1"], ("meta1",)),
    ],
)
def it_has_metadata(target, expected):
    ann = r.annotation(target)
    aa = tuple(ann.metadata)
    assert aa == expected


@pytest.mark.parametrize(
    "target,types,expected",
    [
        (Annotated[int, "meta", 123], (str,), ("meta",)),
        (Annotated[int, "meta", 123, ()], (str, int), ("meta", 123)),
    ],
)
def it_filters_metadata_by_type(target, types, expected):
    ann = r.annotation(target)
    got = tuple(x for x in ann.metadata_of_type(*types))
    assert got == tuple(r.annotation(x) for x in expected)


@pytest.mark.parametrize(
    "target,expected",
    [
        (int, "int"),
        (list[int], "list[int]"),
        (NotRequired[str], "NotRequired[str]"),
        (Annotated[int, "meta"], "Annotated[int, 'meta']"),
        (
            Annotated[NotRequired[str], "meta"],
            "Annotated[NotRequired[str], 'meta']",
        ),
        (Unpack[dict[str, int]], "Unpack[dict[str, int]]"),
    ],
)
def it_stringifies_correctly(target, expected):
    ann = r.annotation(target)
    assert str(ann) == f"⟪ {expected} ⟫"


@pytest.mark.parametrize(
    "target,expected",
    [
        (int, int),
        (list, list),
        (list[int], list),
        (dict[int, str], dict),
        (Example, Example),
        (Example_A, Example_A),
        (Example_A[int], Example_A),
        (Annotated[int, "meta"], Annotated),
        (NotRequired[int], NotRequired),
    ],
)
def it_has_right_origin(target, expected):
    ann = r.annotation(target)
    assert ann.origin == r.annotation(expected)
