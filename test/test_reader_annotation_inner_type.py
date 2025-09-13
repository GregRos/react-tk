import typing
import pytest

from reactk.model2.ants.reflector import Reflector


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
    r = Reflector()
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
    r = Reflector()
    ann = r.annotation(target)
    assert ann.name == expected
