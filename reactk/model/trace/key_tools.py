import re
from typing import Literal


replace_chars_in_key = re.compile(r"[^a-zA-Z0-9_]+")
render_delim = "."

type Display = Literal["log", "safe", "id"]


def key_type_part(key: str, type: type) -> str:
    return f"{type.__name__}({key})"
