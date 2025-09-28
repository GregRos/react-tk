from typing import NotRequired, TypedDict
from expression import Some
from typing_extensions import Annotated

from reactk.props.annotations.prop_meta import prop_meta
from reactk.tk.types.font import Font


class TextProps(TypedDict):
    text: Annotated[NotRequired[str], prop_meta(no_value="", subsection="configure")]
    font: Annotated[NotRequired[Font], prop_meta(repr="simple", no_value=None)]
    foreground: Annotated[
        NotRequired[str], prop_meta(no_value="#ffffff", subsection="configure")
    ]
    justify: Annotated[
        NotRequired[str], prop_meta(no_value="center", subsection="configure")
    ]
    wraplength: Annotated[
        NotRequired[int], prop_meta(no_value=None, subsection="configure")
    ]
