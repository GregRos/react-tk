from reactk.model2.prop_model import PropSection
from reactk.model.props.prop_value import PropValue, format_value
from reactk.model.trace.render_trace import RenderTrace
from reactk.model.trace.render_trace import Display


from collections.abc import Mapping
from typing import Any, Iterator

SAME = object()


class PValues(Mapping[str, "PropValue | PValues"]):
    section: "PropSection"
    _vals: Mapping[str, Any]

    def __init__(
        self,
        props: "PropSection",
        values: Mapping[str, Any] = {},
        old: "PValues | None" = None,
    ):
        self.old = old
        self.section = props
        self._vals = {k: v for k, v in values.items() if v is not None}
        props.assert_valid_value(values)

    def get_trace_name(self, display: Display) -> str:
        trace = self["trace"].value
        assert isinstance(trace, RenderTrace), "Trace must be RenderTrace object"
        return trace.to_string(display)

    def __repr__(self) -> str:
        # FIXME: This is terrible!!!
        # Stringifying this object should be saner
        entries = []
        values = self.items()
        props_first = sorted(values, key=lambda x: not isinstance(x[1], PropValue))
        for key, value in props_first:
            if key == "key" or key == "trace":
                continue

            def fmt(s: Any):
                prop = self.section.props[key]
                if isinstance(prop, PropSection):
                    return s.__repr__()
                match prop.repr:
                    case "none":
                        return ""
                    case "simple":
                        return s.__class__.__name__
                    case "recursive":
                        return format_value(s)

            if self.old is not None and isinstance(value, PropValue):
                # FIXME: format could use some work
                entries += [
                    f"{key}[{fmt(self.old[key].value) if key in self.old else "∅"} ➔  {fmt(value.value)}]"
                ]
                continue
            repr_result = value.__repr__()
            if repr_result:
                entries += [value.__repr__()]
        props = ", ".join(entries)
        name = (
            self.old.get_trace_name("log")
            if self.old
            else self._vals["key"] if "key" in self._vals else self.section.name
        )
        return f"{name}({props})"

    def without(self, *keys: str) -> "PValues":
        return PValues(
            self.section, {k: v for k, v in self._vals.items() if k not in keys}
        )

    def __getitem__(self, key: str) -> "PropValue | PValues":
        value = self._vals.get(key)
        prop = self.section.props[key]
        if value is None:
            if isinstance(prop, PropSection):
                raise KeyError(f"Key {key} is a section, but doesn't exist in values")
            return PropValue(prop, prop.value)
            raise KeyError(f"Key {key} doesn't exist in values")
        if isinstance(prop, PropSection):
            return PValues(prop, value)
        return PropValue(prop, value)

    @property
    def value(self) -> Mapping[str, Any]:
        return self._vals

    def __len__(self) -> int:
        return len(self._vals)

    def __iter__(self) -> Iterator[str]:
        return iter(self._vals)

    def merge(self, other: Mapping[str, Any]) -> "PValues":
        return PValues(self.section, dict(self._vals) | dict(other))

    @staticmethod
    def _diff(a: Any, b: Any) -> Any:
        if isinstance(a, PValues):
            if not isinstance(b, PValues):
                raise ValueError("Cannot diff PropVals with non-PropVals")
            return a.diff(b)
        if isinstance(b, PValues):
            raise ValueError("Cannot diff PropVals with non-PropVals")
        if a == b:
            return SAME
        return b

    def diff(self, other: "PValues") -> "PValues":
        self.section.assert_valid_value(other._vals)
        out = {}
        for k in self.keys() | other.keys():
            if k not in self:
                out[k] = other[k].value
            elif k not in other:
                continue
            v = self[k]
            match v:
                case PropValue():
                    if v != other[k]:
                        out[k] = other[k].value
                case PValues():
                    if v.section.recurse:
                        result = PValues._diff(v, other._vals[k])
                        if result is not SAME:
                            out[k] = result.value
                    else:
                        if v != other[k]:
                            out[k] = other[k].value

        return PValues(self.section, out, old=self)

    def compute(self) -> tuple[str, dict[str, Any]]:
        result = {}
        name = self.section.name

        def get_or_create_section(section: str):
            if section not in result:
                result[section] = {}
            return result[section]

        for key, prop_val in self.items():
            k, v = prop_val.compute()
            target = (
                get_or_create_section(prop_val.prop.subsection)
                if isinstance(prop_val, PropValue) and prop_val.prop.subsection
                else result
            )
            target[k] = v
        return name, result
