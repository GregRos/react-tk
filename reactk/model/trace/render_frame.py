import re
from typing import TYPE_CHECKING, Literal
from reactk.pretty.format_subscript import format_subscript

if TYPE_CHECKING:
    from reactk.model.component import Component
    from reactk.model.shadow_node import ShadowNode

replace_chars_in_key = re.compile(r"[^a-zA-Z0-9_]+")

type Display = Literal["log", "safe", "id"]


class RenderFrame:
    invocation: int

    def __init__(
        self, rendered: "Component | ShadowNode", line_no: int, invocation: int
    ):
        self.invocation = invocation
        # We need to be careful here, since Component/ShadowNode use this object
        # we can't just call random stuff, and we shouldn't store it.
        self.type = rendered.__class__
        self.key = rendered.key
        self.lineno = line_no

    def to_string(self, display: Display) -> str:
        if display == "safe":

            if not self.key:
                result = f"{self.invocation}+{self.lineno}_{self.type.__name__}"
            else:
                result = self.key

            return replace_chars_in_key.sub("_", result).lower()

        pos_part = (
            f":{self.lineno}{format_subscript(self.invocation)}〉"
            if self.invocation >= 0
            else ""
        )
        key_part = f"{self.key}" if self.key else f"{pos_part}{self.type.__name__}"
        return key_part

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RenderFrame):
            return NotImplemented
        return (
            self.invocation == value.invocation
            and self.type == value.type
            and self.key == value.key
            and self.lineno == value.lineno
        )
