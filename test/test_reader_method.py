import pytest

from reactk.model2.ants.reflector import Reflector


def func_with_annotations(a: int, b: str) -> int:
    return 0


def func_without_return(a: int, b: str):
    return 0


def test_name_and_debug_signature():
    r = Reflector()
    m = r.method(func_with_annotations)
    assert m.name == "func_with_annotations"
    # debug signature should include the function name, annotated args and return
    assert m._debug_signature.startswith("func_with_annotations(")
    assert "-> int" in m._debug_signature


def test_target_preserved():
    r = Reflector()
    m = r.method(func_with_annotations)
    # Reader_Method.__post_init__ sets target to the original function if no
    # __reactk_original__ accessor is present; that should be the same object.
    assert m.target is func_with_annotations


def test_arg_index_in_range_and_out_of_range():
    r = Reflector()
    m = r.method(func_with_annotations)
    assert m.arg(0) == r.annotation(int)
    assert m.arg(1) == r.annotation(str)

    with pytest.raises(IndexError):
        m.arg(2)


def test_returns_and_no_return_annotation():
    r = Reflector()
    m = r.method(func_with_annotations)
    assert m.returns() == r.annotation(int)

    with pytest.raises(KeyError):
        r.method(func_without_return).returns()
