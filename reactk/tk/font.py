from typing import Annotated, NotRequired, TypedDict

from reactk.model.props.prop import Prop


class Font(TypedDict):
    family: str
    size: int
    style: Annotated[NotRequired[str], Prop(no_value="normal")]


def to_tk_font(font: Font):
    return (font["family"], font["size"], font.get("style", "normal"))
