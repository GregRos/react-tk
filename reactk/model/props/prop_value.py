from dataclasses import dataclass, field
from reactk.model.props.prop import Prop


from typing import Any, TypeGuard, override


def format_value(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


class PropValue:
    __match_args__ = ("value", "prop")

    def __init__(self, prop: Prop, value: Any) -> None:
        self.prop = prop
        self.value = value

    def __repr__(self) -> str:
        match self.prop.repr:
            case "none":
                return ""
            case "simple":
                return f"{self.prop.name}={self.value.__class__.__name__}"
            case "recursive":
                return f"{self.prop.name}={format_value(self.value)}"
            case _:
                raise ValueError(f"Invalid repr mode: {self.prop.repr}")

    def compute(self) -> tuple[str, Any]:
        v = self.value or self.prop.no_value
        v = self.prop.converter(v) if self.prop.converter else v
        k = self.prop.name or ""
        return k, v

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, PropValue)
            and self.prop == other.prop
            and self.value == other.value
        )
