from reactk.model2.prop_model.prop import Prop, Prop_Schema


def it_schema():
    s = Prop_Schema(
        path=("a",),
        name="A",
        props=[
            Prop(computed_name="Z", name="Y", value_type=int, path=()),
            Prop(computed_name="W", name="X", value_type=str, path=()),
        ],
    )

    assert s[0].name == "Z"
