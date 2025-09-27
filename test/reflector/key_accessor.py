import pytest

from reactk.reflect.accessor.base import KeyAccessor


class WithAttr:
    # declare attribute for type checkers; value set in __init__
    attr = 123


class WithoutAttr:
    attr: int


class SimpleAccessor(KeyAccessor[int]):
    @property
    def key(self) -> str:
        return "attr"


class KeyAccessor_Test:
    # class attributes holding example objects and their accessors
    w: WithAttr
    wo: WithoutAttr
    accessor: SimpleAccessor
    accessor_wo: SimpleAccessor

    def setup_method(self) -> None:
        self.w = WithAttr()
        self.wo = WithoutAttr()
        self.accessor = SimpleAccessor(self.w)
        self.accessor_wo = SimpleAccessor(self.wo)

    def it_gets_when_attr_exists(self):
        assert self.accessor.get() == 123

    def it_gets_raises_when_missing(self):
        with pytest.raises(AttributeError):
            self.accessor_wo.get()

    def it_gets_with_default(self):
        assert self.accessor_wo.get(456) == 456

    def it_sets_overwrites_existing(self):
        self.accessor.set(1011)
        assert self.w.attr == 1011

    def it_sets_creates_new(self):
        self.accessor_wo.set(101112)
        assert self.wo.attr == 101112

    def it_has_key_when_exists(self):
        assert self.accessor.has_key is True

    def it_has_key_when_not_exists(self):
        assert self.accessor_wo.has_key is False

    def it_bool_when_exists(self):
        assert bool(self.accessor) is True

    def it_bool_when_not_exists(self):
        assert bool(self.accessor_wo) is False
