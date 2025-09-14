import pytest

from reactk.model2.ants.reflector import Reflector


class Sample:
    x: int
    y: str

    def method_a(self, a: int) -> int:
        return a

    def method_b(self, b: str) -> str:
        return b


r = Reflector()


def test_target_preserved():
    tr = r.type(Sample)
    assert tr.target is Sample


def test_annotations_all():
    tr = r.type(Sample)
    ann_map = tr.annotations
    assert isinstance(ann_map, dict)
    assert "x" in ann_map and "y" in ann_map
    assert ann_map["x"].target is int
    assert ann_map["y"].target is str


def test_methods_all():
    tr = r.type(Sample)
    methods = tr.methods
    # methods mapping should include method_a and method_b
    assert "method_a" in methods
    assert "method_b" in methods


def test_get_annotation_exists_and_missing():
    tr = r.type(Sample)
    # existing
    ann = tr.annotation("x")
    assert ann.target is int
    # missing should raise KeyError
    with pytest.raises(KeyError):
        tr.annotation("nope")


def test_method_exists_and_missing():
    tr = r.type(Sample)
    m = tr.method("method_a")
    assert m.name == "method_a"
    with pytest.raises(KeyError):
        tr.method("nope")


# Module-scope classes for inherited-case tests: use `Sample` as the base class
# `Sample` is defined above in this module and already provides annotations and methods
class Inherited(Sample):
    b: str

    def own_method(self, s: str) -> str:
        return s


def test_inherited_methods_inclusion():
    tr_inh = r.type(Inherited)
    methods = tr_inh.methods
    # should include inherited Sample methods and Inherited's own method
    assert "method_a" in methods
    assert "method_b" in methods
    assert "own_method" in methods


def test_inherited_annotations_inclusion():
    tr_inh = r.type(Inherited)
    ann = tr_inh.annotations
    # should include Sample's annotations and Inherited's own annotation
    assert "x" in ann and "y" in ann and "b" in ann


def test_inherited_annotation_retrieval():
    tr_inh = r.type(Inherited)
    ann_x = tr_inh.annotation("x")
    assert ann_x.target is int
    ann_y = tr_inh.annotation("y")
    assert ann_y.target is str
    ann_b = tr_inh.annotation("b")
    assert ann_b.target is str


def test_inherited_method_retrieval():
    tr_inh = r.type(Inherited)
    m_a = tr_inh.method("method_a")
    assert m_a.name == "method_a"
    m_b = tr_inh.method("method_b")
    assert m_b.name == "method_b"
    m_own = tr_inh.method("own_method")
    assert m_own.name == "own_method"
