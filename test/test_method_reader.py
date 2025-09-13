import inspect
from types import MethodType

import pytest

from reactk.model2.ants.key_accessor import KeyAccessor
from reactk.model2.ants.readers import Reader_Method, Reader_Annotation


def sample_function(a: int, b: str) -> bool:
    return True


def test_reader_method_basic_annotations():
    rm = Reader_Method(sample_function)
    # name should match the function name
    assert rm.name == sample_function.__name__

    # return annotation should be readable
    ret = rm.get_return()
    assert isinstance(ret, Reader_Annotation)
    assert ret.target is bool
    assert str(ret)  # saneness

    # args by position and name
    a_ann = rm.get_arg(0)
    b_ann = rm.get_arg(1)
    assert str(a_ann) and str(b_ann)


def test_get_arg_raises_on_invalid():
    rm = Reader_Method(sample_function)
    with pytest.raises(KeyError):
        rm.get_arg(99)
    with pytest.raises(KeyError):
        rm.get_arg("nonexistent")


def test_orig_accessor_uses_original_when_present():
    # create a wrapper object that stores original under __reactk_original__
    def original(x: int) -> int:
        return x + 1

    def wrapper(x: int) -> int:
        return original(x) * 2

    # attach the original attribute in the wrapper
    setattr(wrapper, "__reactk_original__", original)

    rm = Reader_Method(wrapper)
    # Reader_Method should expose the original for name/signature purposes
    assert rm.name == original.__name__
    # debug signature should reflect the original function's signature
    assert "x" in rm._debug_signature
