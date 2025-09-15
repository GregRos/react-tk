from typing import Annotated, Unpack, NotRequired, Required, Union
import pytest

from reactk.model2.ants.reflector import Reflector

r = Reflector()


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
def test_inner_type(target, expected):
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
def test_name(target, expected):
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
def test_inner_type_reader(target, expected):
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
def test_metadata(target, expected):
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
def test_metadata_of_type(target, types, expected):
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
def test_str(target, expected):
    ann = r.annotation(target)
    assert str(ann) == f"⟪ {expected} ⟫"


class Example:
    pass


class Example_A[A]:
    pass


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
def test_origin(target, expected):
    ann = r.annotation(target)
    assert ann.origin == r.annotation(expected)
