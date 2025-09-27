import re
from dataclasses import dataclass
from types import FrameType
from typing import TYPE_CHECKING, Literal
from inspect import getframeinfo, stack, FrameInfo, currentframe

from reactk.model2.ants.key_accessor import KeyAccessor
from reactk.model2.util.str import format_subscript

if TYPE_CHECKING:
    from reactk.model.component import Component
    from reactk.model.shadow_node import ShadowNode

replace_chars_in_key = re.compile(r"[^a-zA-Z0-9_]+")
starts_with_non_breaking = re.compile(r"^[^a-zA-Z0-9_]")
render_delim = "."

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


class RenderTrace:
    frames: tuple[RenderFrame, ...]

    def __init__(self, *frames: RenderFrame):
        self.frames = frames

    def __add__(self, other: "RenderTrace | RenderFrame") -> "RenderTrace":
        if isinstance(other, RenderFrame):
            return RenderTrace(*self.frames, other)
        return RenderTrace(*self.frames, *other.frames)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RenderTrace):
            return NotImplemented
        return self.frames == value.frames

    def to_string(self, display: Display) -> str:
        parts = [frame.to_string(display) for frame in self.frames]
        result = ""
        for part in parts:
            if result and not starts_with_non_breaking.search(part):
                result += render_delim if display != "safe" else "__"

            result += part

        return result


class RenderTraceAccessor(KeyAccessor[RenderTrace]):
    @property
    def key(self) -> str:
        return "_TRACE"
