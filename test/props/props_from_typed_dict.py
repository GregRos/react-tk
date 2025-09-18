from typing import Annotated, TypedDict

from expression import Nothing, Some
from reactk.model2.prop_ants import prop_meta, schema_meta
from reactk.model2.prop_ants.create_props import read_props_from_top_class
from reactk.model2.prop_model.prop import Prop, Prop_Schema, Prop_Value
from reactk.model2.util.dict import dict_equal


class One_Annotated_Prop(TypedDict):
    b: Annotated[
        str,
        prop_meta(
            name="__b__",
            no_value="",
            converter=str,
            repr="never",
            subsection="configure",
            metadata={"x": 5},
        ),
    ]


class One_Annotated_Schema(TypedDict):
    a: Annotated[
        One_Annotated_Prop, schema_meta(name="__a__", repr="never", metadata={"x": 5})
    ]


class One_Unannotated_Prop(TypedDict):
    b: str


def it_works_for_simple_typed_dict():

    a = read_props_from_top_class(One_Annotated_Prop)
    a_b = a["b"]
    assert isinstance(a_b, Prop)
    assert a_b.computed_name == "__b__"
    assert a_b.no_value == Some("")
    assert a_b.converter is str
    assert a_b.subsection == "configure"
    assert a_b.repr == "never"
    assert a_b.value_type == str
    assert a_b.is_required is False
    assert a_b.path == (One_Annotated_Prop.__name__,)
    assert dict_equal(a_b.metadata, {"x": 5})


def it_works_for_unannotated_typed_dict():
    a = read_props_from_top_class(One_Unannotated_Prop)
    a_b = a["b"]
    assert isinstance(a_b, Prop)
    assert a_b.computed_name == None
    assert a_b.no_value is Nothing
    assert a_b.value_type == str
    assert a_b.converter is None
    assert a_b.subsection is None
    assert a_b.repr == "recursive"
    assert a_b.is_required is True
    assert a_b.path == (One_Unannotated_Prop.__name__,)


def it_creates_nested_schema():

    a = read_props_from_top_class(One_Annotated_Schema)
    a_a = a["a"]
    assert isinstance(a_a, Prop_Schema)
    assert a_a.computed_name == "__a__"
    assert a_a.path == (One_Annotated_Schema.__name__,)
    assert a_a.repr == "never"
    assert dict_equal(a_a.metadata, {"x": 5})


def it_creates_prop_in_nested_schema():
    a = read_props_from_top_class(One_Annotated_Schema)
    a_a = a["a"]
    assert isinstance(a_a, Prop_Schema)
    a_a_b = a_a["b"]
    assert isinstance(a_a_b, Prop)
    assert a_a_b.computed_name == "__b__"
    assert a_a_b.no_value == Some("")
    assert a_a_b.value_type == str
    assert a_a_b.repr == "never"
    assert a_a_b.is_required is False
    assert a_a_b.path == (One_Annotated_Schema.__name__, "a")
