import pytest

from typing import TypeVar

from reactk.model2.ants.reflector import Reflector


r = Reflector()

# Module-level Reader_TypeVar instances created inline (avoid assigning TypeVar to
# differently-named variables which some linters complain about)
RA = r.type_var(TypeVar("A"))
RExtra = r.type_var(TypeVar("Extra"))
RB = r.type_var(TypeVar("B", bound=int))
RC = r.type_var(TypeVar("C", default=str))


@pytest.mark.parametrize(
    "reader,expected",
    [
        (RA, "A"),
        (RB, "B"),
        (RC, "C"),
    ],
)
def test_name(reader, expected):
    assert reader.name == expected


@pytest.mark.parametrize(
    "reader,expected",
    [
        (RA, None),
        (RB, r.type(int)),
        (RC, None),
    ],
)
def test_bound(reader, expected):
    return reader == expected


@pytest.mark.parametrize(
    "reader,expected",
    [
        (RA, None),
        (RB, None),
        (RC, r.type(str)),
    ],
)
def test_default(reader, expected):
    assert reader.default == expected


@pytest.mark.parametrize(
    "reader,expected",
    [
        (RA, "A"),
        (RB, "B: int"),
        (RC, "C = str"),
    ],
)
def test_str(reader, expected):
    assert str(reader) == expected


@pytest.mark.parametrize(
    "reader,other,expected",
    [
        (RA, r.type_var(TypeVar("A")), True),
        (RA, RExtra, False),
        (RB, r.type_var(TypeVar("B", bound=int)), True),
        (RB, RExtra, False),
        (RC, r.type_var(TypeVar("C", default=str)), True),
        (RC, RExtra, False),
    ],
)
def test_is_similar(reader, other, expected):
    assert reader.is_similar(other) is expected
