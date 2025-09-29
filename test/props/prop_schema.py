from expression import Nothing, Some
import pytest
from react_tk.props.impl.prop import (
    Prop,
    Prop_ComputedMapping,
    Prop_Mapping,
    Prop_Schema,
    Prop_Value,
)

two_props = Prop_Schema(
    path=("a",),
    name="A",
    props=[
        Prop(name="Y", value_type=int, path=(), computed_name="__Y__"),
        Prop(name="X", value_type=str, path=(), computed_name="__X__"),
    ],
)

all_optional = Prop_Schema(
    path=("a",),
    name="A",
    props=[
        Prop(
            name="Y", value_type=int, path=(), computed_name="__Y__", no_value=Some(0)
        ),
        Prop(
            name="X", value_type=str, path=(), computed_name="__X__", no_value=Some("")
        ),
    ],
)


def it_has_props():
    assert two_props["Y"].name == "Y"
    assert two_props["X"].name == "X"


def it_throws_for_missing_prop():
    with pytest.raises(KeyError):
        two_props["Z"]


def it_accepts_valid_dict():
    valid_dict = {
        "Y": 5,
        "X": "hello",
    }
    assert two_props.is_valid(valid_dict)
    two_props.assert_valid(valid_dict)


def it_rejects_invalid_dict():

    invalid_dict = {
        "Y": "nope",
        "X": "hello",
    }
    assert not two_props.is_valid(invalid_dict)
    with pytest.raises(ValueError):
        two_props.assert_valid(invalid_dict)


def it_lets_iterate():
    names = {p.name for p in two_props}
    assert names == {"X", "Y"}


def it_reports_length():
    assert len(two_props) == 2


def it_reports_required():
    assert two_props.is_required
    assert not two_props.is_valid({})
    assert all(p.is_required for p in two_props)


def it_reports_all_optional():
    assert all_optional.is_valid({})
    all_optional.assert_valid({})


def it_adds_props_via_update():
    new_props = two_props.update(
        [Prop(name="Z", value_type=float, path=(), computed_name="__Z__")]
    )
    assert len(new_props) == 3
    assert new_props["Z"].name == "Z"
    assert len(two_props) == 2  # original unchanged
    assert {*new_props.keys()} == {"X", "Y", "Z"}


class PropMapping_Test:
    @property
    def mapping(self) -> Prop_Mapping:
        return two_props({"X": "hi", "Y": 3})

    def it_has_schema(self):
        assert self.mapping.prop is two_props

    def it_allows_keyed_access(self):
        x_prop_value = self.mapping["X"]
        assert isinstance(x_prop_value, Prop_Value)
        assert x_prop_value.prop is two_props["X"]
        assert x_prop_value.value == Some("hi")

    def it_iterates_values(self):
        names = {pv.prop.name for pv in self.mapping}
        assert names == {"X", "Y"}

    def it_computes(self):
        result = self.mapping.compute()
        assert isinstance(result, Prop_ComputedMapping)
        assert result == {"__X__": "hi", "__Y__": 3}

    def it_runs_converters(self):
        extra_prop = two_props.update(
            [
                Prop(
                    name="Z",
                    value_type=int,
                    path=(),
                    computed_name="__Z__",
                    converter=lambda v: v * 2,
                )
            ]
        )
        mapping = extra_prop({"X": "hi", "Y": 3, "Z": 3})
        result = mapping.compute()
        assert result == {"__X__": "hi", "__Y__": 3, "__Z__": 6}

    def it_uses_defaults(self):
        optional = all_optional.with_values({"X": "hi"})
        missing_prop = optional["Y"]
        assert isinstance(missing_prop, Prop_Value)
        assert missing_prop.is_missing
        assert missing_prop.value is Nothing

    def it_overwrites_value(self):
        updated = self.mapping.update({"X": "there"})
        x_prop = updated["X"]
        assert isinstance(x_prop, Prop_Value)
        assert x_prop.value == Some("there")
        assert x_prop.old == Some("hi")
        y_prop = updated["Y"]
        assert isinstance(y_prop, Prop_Value)
        assert y_prop.value == Some(3)

    def it_validates_on_update(self):
        with pytest.raises(ValueError):
            self.mapping.update({"Y": "nope"})

        with pytest.raises(ValueError):
            self.mapping.update({"Z": 5})  # Z not in schema

    def it_diffs_another_mapping(self):
        other = two_props({"X": "there", "Y": 3})
        diff = self.mapping.diff(other)
        assert isinstance(diff, Prop_ComputedMapping)
        assert diff == {"__X__": "there"}

    def it_diffs_keyed_values(self):
        other = two_props({"X": "hi", "Y": 5})
        diff = self.mapping.diff(other)
        assert isinstance(diff, Prop_ComputedMapping)
        assert diff == {"__Y__": 5}

    def it_diffs_to_empty(self):
        other = two_props({"X": "hi", "Y": 3})
        diff = self.mapping.diff(other)
        assert isinstance(diff, Prop_ComputedMapping)
        assert diff == {}
