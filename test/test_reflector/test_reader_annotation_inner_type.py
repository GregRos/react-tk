import typing
import pytest

from reactk.model2.ants.reflector import Reflector

r = Reflector()


@pytest.mark.parametrize(
    "target,expected",
    [
        (int, int),
        (list[int], list[int]),
        (dict[str, int], dict[str, int]),
        (typing.Annotated[int, "meta"], int),
        (typing.Unpack[dict[str, int]], dict[str, int]),
        (typing.NotRequired[int], int),
        (typing.Annotated[typing.Unpack[dict[str, int]], "meta"], dict[str, int]),
        (typing.Required[int], int),
        (typing.Annotated[typing.NotRequired[int], "meta"], int),
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
        (typing.Annotated[int, "meta"], "Annotated"),
        (typing.Unpack[dict[str, int]], "Unpack"),
        (typing.NotRequired[int], "NotRequired"),
        (typing.Union[int, str], "Union"),
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
        (typing.Annotated[int, "meta"], ("meta",)),
        (typing.Annotated[list[int], "meta1", "meta2"], ("meta1", "meta2")),
        (typing.Annotated[typing.NotRequired[int], "meta1"], ("meta1",)),
    ],
)
def test_metadata(target, expected):
    ann = r.annotation(target)
    aa = tuple(ann.metadata)
    assert aa == expected


@pytest.mark.parametrize(
    "target,types,expected",
    [
        (typing.Annotated[int, "meta", 123], (str,), ("meta",)),
        (typing.Annotated[int, "meta", 123, ()], (str, int), ("meta", 123)),
    ],
)
def test_metadata_of_type(target, types, expected):
    ann = r.annotation(target)
    got = tuple(x for x in ann.metadata_of_type(*types))
    assert got == tuple(r.annotation(x) for x in expected)
