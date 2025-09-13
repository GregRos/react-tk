import pytest

from reactk.model2.ants.key_accessor import KeyAccessor


class WithAttr:
    # declare attribute for type checkers; value set in __init__
    attr = 123


class WithoutAttr:
    attr: int


class SimpleAccessor(KeyAccessor[int]):
    @property
    def key(self) -> str:
        return "attr"


def make_with():
    """Create a fresh WithAttr instance and its accessor."""
    w = WithAttr()
    a = SimpleAccessor(w)
    return w, a


def make_without():
    """Create a fresh WithoutAttr instance and its accessor."""
    wo = WithoutAttr()
    a = SimpleAccessor(wo)
    return wo, a


def test_get_when_attr_exists():
    _, accessor = make_with()
    assert accessor.get() == 123


def test_get_raises_when_missing():
    _, accessor = make_without()
    with pytest.raises(AttributeError):
        accessor.get()


def test_get_with_default():
    _, accessor = make_without()
    assert accessor.get(456) == 456


def test_set_overwrites_existing():
    w, accessor = make_with()
    accessor.set(1011)
    assert w.attr == 1011


def test_set_creates_new():
    wo, accessor = make_without()
    accessor.set(101112)
    assert wo.attr == 101112


def test_has_key_when_exists():
    _, accessor = make_with()
    assert accessor.has_key is True


def test_has_key_when_not_exists():
    _, accessor = make_without()
    assert accessor.has_key is False


def test_bool_when_exists():
    _, accessor = make_with()
    assert bool(accessor) is True


def test_bool_when_not_exists():
    _, accessor = make_without()
    assert bool(accessor) is False
