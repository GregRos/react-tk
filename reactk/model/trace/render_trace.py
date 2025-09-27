from dataclasses import dataclass
import re
from types import FrameType
from typing import TYPE_CHECKING, Literal
from inspect import getframeinfo, stack, FrameInfo, currentframe

from reactk.model2.ants.key_accessor import KeyAccessor

from .key_tools import Display, render_delim
from reactk.model.trace.render_frame import RenderFrame


starts_with_non_breaking = re.compile(r"^[^a-zA-Z0-9_]")


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
