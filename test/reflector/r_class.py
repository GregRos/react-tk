import pytest

from reactk.model2.ants.reflector import Reflector


class Sample:
    x: int
    y: str

    def method_a(self, a: int) -> int:
        return a

    def method_b(self, b: str) -> str:
        return b


class Inherited(Sample):
    b: str

    def own_method(self, s: str) -> str:
        return s


class Sample2:
    pass


class MultiBase(Sample, Sample2):
    pass


r: Reflector = Reflector()


def it_preserves_target():
    tr = r.type(Sample)
    assert tr.target is Sample


def it_reports_all_annotations():
    tr = r.type(Sample)
    ann_map = tr.annotations
    assert isinstance(ann_map, dict)
    assert "x" in ann_map and "y" in ann_map
    assert ann_map["x"].target is int
    assert ann_map["y"].target is str


def it_reports_all_methods():
    tr = r.type(Sample)
    methods = tr.methods
    # methods mapping should include method_a and method_b
    assert "method_a" in methods
    assert "method_b" in methods


def it_handles_annotation_lookup():
    tr = r.type(Sample)
    # existing
    ann = tr.annotation("x")
    assert ann.target is int
    # missing should raise KeyError
    with pytest.raises(KeyError):
        tr.annotation("nope")


def it_handles_method_lookup():
    tr = r.type(Sample)
    m = tr.method("method_a")
    assert m.name == "method_a"
    with pytest.raises(KeyError):
        tr.method("nope")


def it_includes_inherited_methods():
    tr_inh = r.type(Inherited)
    methods = tr_inh.methods
    # should include inherited Sample methods and Inherited's own method
    assert "method_a" in methods
    assert "method_b" in methods
    assert "own_method" in methods


def it_includes_inherited_annotations():
    tr_inh = r.type(Inherited)
    ann = tr_inh.annotations
    # should include Sample's annotations and Inherited's own annotation
    assert "x" in ann and "y" in ann and "b" in ann


def it_retrieves_inherited_annotations():
    tr_inh = r.type(Inherited)
    ann_x = tr_inh.annotation("x")
    assert ann_x.target is int
    ann_y = tr_inh.annotation("y")
    assert ann_y.target is str
    ann_b = tr_inh.annotation("b")
    assert ann_b.target is str


def it_retrieves_inherited_methods():
    tr_inh = r.type(Inherited)
    m_a = tr_inh.method("method_a")
    assert m_a.name == "method_a"
    m_b = tr_inh.method("method_b")
    assert m_b.name == "method_b"
    m_own = tr_inh.method("own_method")
    assert m_own.name == "own_method"


def it_retrieves_single_base():
    tr = r.type(Inherited)
    bases = set(tr.bases)
    assert bases == {r.type(Sample)}


def it_retrieves_base_annotations_without_generics():
    tr = r.type(Inherited)
    base_anns = set(tr.base_annotations)
    assert base_anns == {r.annotation(Sample)}


def it_retrieves_no_bases():
    tr = r.type(Sample)
    bases = set(tr.bases)
    assert bases == {r.type(object)}


def it_retrieves_base_annotations():
    class InheritedGeneric(list[int]):
        pass

    tr = r.type(InheritedGeneric)
    base_anns = set(tr.base_annotations)
    assert base_anns == {r.annotation(list[int])}


def it_retrieves_multiple_bases():

    tr = r.type(MultiBase)
    bases = set(tr.bases)
    assert bases == {r.type(Sample), r.type(Sample2)}
    assert set(tr.base_annotations) == {r.annotation(Sample), r.annotation(Sample2)}
