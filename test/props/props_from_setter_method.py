from typing import Annotated, TypedDict, Unpack

from expression import Some

from reactk.model.props.annotations import prop_meta
from reactk.model.props.annotations.create_props import read_props_from_top_class
from reactk.model.props.annotations.decorators import _HasMerge, schema_setter
from reactk.model.props.impl.prop import Prop, Prop_Schema
from reactk.util.dict import dict_equal


class One_Annotated_Prop(TypedDict):
    b: Annotated[
        str,
        prop_meta(
            converter=str,
            name="__b__",
            no_value="",
            subsection="configure",
            repr="never",
            metadata={"x": 5},
        ),
    ]


class One_Setter_Method_With_Dict(_HasMerge):
    @schema_setter(repr="never", name="__Stuff__", metadata={"x": 5})
    def Stuff(self, **stuff: Unpack[One_Annotated_Prop]) -> None: ...


def it_works_for_setter_method():
    props = read_props_from_top_class(One_Setter_Method_With_Dict)
    assert isinstance(props, Prop_Schema)
    assert props.name == "One_Setter_Method_With_Dict"
    stuff = props["Stuff"]
    assert isinstance(stuff, Prop_Schema)
    assert stuff.name == "Stuff"
    assert stuff.path == ("One_Setter_Method_With_Dict",)
    assert stuff.repr == "never"
    assert dict_equal(stuff.metadata, {"x": 5})
    stuff_b = stuff["b"]
    assert isinstance(stuff_b, Prop)
    assert stuff_b.computed_name == "__b__"
    assert stuff_b.no_value == Some("")
    assert stuff_b.converter is str
    assert stuff_b.subsection == "configure"
    assert stuff_b.repr == "never"
    assert stuff_b.value_type == str
    assert stuff_b.is_required is False
