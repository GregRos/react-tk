from typing import Annotated, NotRequired, TypedDict

from reactk.model2.prop_ants import prop_meta


class Font(TypedDict):
    family: str
    size: int
    style: Annotated[NotRequired[str], prop_meta(no_value="normal")]


def to_tk_font(font: Font):
    return (font["family"], font["size"], font.get("style", "normal"))
