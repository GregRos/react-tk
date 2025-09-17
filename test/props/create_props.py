"""
Tests for interacting diirectly with Prop, PropSection, PValues, PDiff, PropValue.
"""

from expression import Option, Some, Nothing
import pytest
from typeguard import value
from reactk.model2.prop_model.prop import Prop, Prop_Value


def it_works_for_required_Prop():
    p = Prop(name="A", value_type=int, path=())
    assert p.name == "A"
    assert p.is_required
    assert p.path == ()
    assert p.is_valid(5)
    assert not p.is_valid("x")
    with pytest.raises(ValueError):
        p.assert_valid("x")
    p.assert_valid(5)
    assert p != Prop(name="A", value_type=int, path=())


def it_works_for_optional_Prop():
    p = Prop(name="A", value_type=int, path=(), no_value=Some(0))
    assert not p.is_required


def it_required_PropValue():
    p = Prop(name="A", value_type=int, path=(), converter=lambda x: x + 1)
    pv = p(Some(5))
    assert pv.prop is p
    assert pv.value == Some(5)
    assert pv.old is Nothing
    assert pv.compute() == 6
    assert pv == p.to_value(5)
    updated = pv.update(10)
    assert updated.old == Some(5)
    assert updated.value == Some(10)
    assert updated.compute() == 11
    match pv:
        case Prop_Value(Option(), p2):
            assert p2 is p
        case _:
            assert False, "Should have matched"


def it_optional_PropValue_no_value():
    p = Prop(name="A", value_type=int, path=(), no_value=Some(5))
    pv = p.to_value()
    assert pv.is_missing
    assert pv.value is Nothing
    assert pv.compute() == 5


def it_optional_PropValue_with_value():
    p = Prop(name="A", value_type=int, path=(), no_value=Some(5))
    pv = p.to_value(10)
    assert not pv.is_missing
    assert pv.value == Some(10)
    assert pv.compute() == 10


def it_fails_to_create_PropValue_for_required_Prop_with_no_value():
    p = Prop(name="A", value_type=int, path=())
    with pytest.raises(ValueError):
        p.to_value()
    with pytest.raises(ValueError):
        Prop_Value(prop=p, value=Nothing)
