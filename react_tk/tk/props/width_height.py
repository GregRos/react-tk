from react_tk.props.annotations import prop_meta


from typing import Annotated, NotRequired, TypedDict


class WidthHeightProps(TypedDict):
    width: Annotated[NotRequired[int], prop_meta(no_value=None)]
    height: Annotated[NotRequired[int], prop_meta(no_value=None)]
