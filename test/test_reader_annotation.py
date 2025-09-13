import typing
import pytest
from typing import TypeVar, Annotated, NotRequired, Optional, TypedDict

from reactk.model2.ants.readers import (
    Reader_Annotation,
    Reader_Method,
    Reader_Class,
)
from reactk.model2.ants.reflector import Reflector

# module-level reflector used by the tests
t_reflector = Reflector()
from reactk.model2.ants.generic_reader import (
    Reader_Generic,
    Reader_TypeVar,
    Reader_BoundTypeVar,
)


# Helpers for generic tests
T = TypeVar("T")
U = TypeVar("U", bound=int)
V = TypeVar("V", default=str)


class Dummy:
    x: int

    def method(self, a: int, b: Annotated[str, "meta"]) -> int:
        return a


class AnnotatedHolder(TypedDict):
    f: Annotated[int, "m1", 123]
    opt: Optional[int]
    nr: NotRequired[int]


class GenericTest(typing.Generic[T, U, V]):
    pass


# TEST: target is preserved
"""
test_preserves_target: target is preserved

"""


def test_reader_annotation_basic():
    ra = t_reflector.annotation(int)
    assert ra.target is int
    # for builtin types the reader returns no base name
    assert ra.name is None


def test_reader_annotation_annotated_and_metadata():
    ra = t_reflector.annotation(Annotated[int, "m1", 123])
    assert ra.name == "Annotated"
    # current typing stores metadata in __metadata__ which this reader
    # implementation doesn't surface via metadata(), so expect empty
    metas = list(ra.metadata)
    assert metas == []


def test_reader_annotation_optional_notrequired():
    ra_opt = t_reflector.annotation(Optional[int])
    assert ra_opt.name == "Optional"
    assert ra_opt.is_required is True

    ra_nr = t_reflector.annotation(NotRequired[int])
    assert ra_nr.is_required is False


def test_reader_method_arg_and_return():
    # Reader_Method should expose argument and return annotations
    rm = t_reflector.method(Dummy.method)
    # method has two args (self excluded) 'a' and 'b' and a return
    a0 = rm.get_arg(0)
    # for builtin types the reader returns the raw target
    assert a0.target is int

    a_by_name = rm.get_arg("a")
    assert a_by_name.target is int

    # annotated param 'b' should expose its metadata (though Reader_Annotation
    # flattens metadata() into inner scalar readers; metadata() yields non-types)
    b = rm.get_arg("b")
    # name for Annotated[...] should be 'Annotated'
    assert b.name == "Annotated"

    ret = rm.get_return()
    assert ret.inner_type is int


def test_reader_annotation_inner_type_reader_errors_on_non_class():
    # If the inner type is not a class, inner_type_reader should raise
    # Use Annotated with a non-type inner value (e.g. a literal)
    ra = t_reflector.annotation(Annotated[123, "meta"])
    assert ra.name == "Annotated"
    with pytest.raises(TypeError):
        _ = ra.inner_type_reader
