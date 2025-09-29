import pytest

from typing import TypeVar

from react_tk.reflect.reflector import Reflector

# Move Reflector and TypeVar readers to module scope
r: Reflector = Reflector()

# Module-level Reader_TypeVar instances created inline (avoid assigning TypeVar to
# differently-named variables which some linters complain about)
RA = r.type_var(TypeVar("A"))
RExtra = r.type_var(TypeVar("Extra"))
RB = r.type_var(TypeVar("B", bound=int))
RC = r.type_var(TypeVar("C", default=str))
RD = r.type_var(TypeVar("D", bound=str, default=str))


@pytest.mark.parametrize(
    "reader,expected",
    [
        (RA, "A"),
        (RB, "B"),
        (RC, "C"),
        (RD, "D"),
    ],
)
def it_reports_name(reader, expected):
    assert reader.name == expected


@pytest.mark.parametrize(
    "reader,expected",
    [
        (RA.with_value(str), r.annotation(str)),
        (RB.with_value(int), r.annotation(int)),
        (RC.with_value(bool), r.annotation(bool)),
        (RD.with_value(str), r.annotation(str)),
    ],
)
def it_reports_bound_value(reader, expected):
    assert reader.value == expected


@pytest.mark.parametrize(
    "reader,expected",
    [
        (RA, None),
        (RB, None),
        (RC, r.annotation(str)),
        (RD, r.annotation(str)),
    ],
)
def it_reports_default(reader, expected):
    assert reader.default == expected


@pytest.mark.parametrize(
    "reader,expected",
    [
        (RA, "A"),
        (RB, "B: int"),
        (RC, "C = str"),
        (RD, "D: str = str"),
    ],
)
def it_stringifies(reader, expected):
    assert str(reader) == f"⟪ {expected} ⟫"


@pytest.mark.parametrize(
    "reader,other,expected",
    [
        (RA, r.type_var(TypeVar("A")), True),
        (RA, RExtra, False),
        (RB, r.type_var(TypeVar("B", bound=int)), True),
        (RB, RExtra, False),
        (RC, r.type_var(TypeVar("C", default=str)), True),
        (RC, RExtra, False),
        (RD, r.type_var(TypeVar("D", bound=str, default=str)), True),
        (RD, RExtra, False),
    ],
)
def it_compares_similarity(reader, other, expected):
    assert reader.is_similar_to(other) is expected


@pytest.mark.parametrize(
    "reader,expected",
    [
        (RA.with_value(str), "A ≡ str"),
        (RB.with_value(int), "B: int ≡ int"),
        (RC.with_value(str), "C ≡ str"),
        (RD.with_value(str), "D: str ≡ str"),
    ],
)
def it_shows_type_arg_str(reader, expected):
    assert str(reader) == f"⟪ {expected} ⟫"
