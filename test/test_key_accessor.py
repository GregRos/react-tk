import pytest
from reactk.model2.util.missing import MISSING
from reactk.model2.ants.key_accessor import KeyAccessor


class Dummy:
    pass


class AttrAccessor(KeyAccessor[int]):
    @property
    def key(self) -> str:
        return "_value"


class BadSetTarget:
    def __init__(self):
        # define property that raises on set
        class _Bad:
            @property
            def _value(self):
                return 1

            @_value.setter
            def _value(self, v):
                raise RuntimeError("cannot set")

        self._bad = _Bad()


def test_get_set_and_has_key():
    d = Dummy()
    a = AttrAccessor(d)
    assert not a.has_key
    assert not a

    # set value
    a.set(10)
    assert a.has_key
    assert a
    assert getattr(d, "_value") == 10

    # get existing
    assert a.get() == 10

    # get with default when missing
    d2 = Dummy()
    a2 = AttrAccessor(d2)
    assert a2.get(5) == 5


def test_get_raises_when_missing():
    d = Dummy()
    a = AttrAccessor(d)
    with pytest.raises(AttributeError):
        a.get()


def test_str_contains_key():
    d = Dummy()
    a = AttrAccessor(d)
    s = str(a)
    assert "_value" in s


def test_set_ignores_exception():
    bad = BadSetTarget()

    # accessor pointing at the inner object that raises on set
    class BadAccessor(KeyAccessor[int]):
        @property
        def key(self) -> str:
            return "_value"

    acc = BadAccessor(bad._bad)
    # should not raise despite underlying setter raising
    acc.set(3)
    # since setter raised, has_key may remain True (attribute exists) or False
    # but no exception should be propagated
