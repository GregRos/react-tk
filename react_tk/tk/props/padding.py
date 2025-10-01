from typing import Annotated, NotRequired, TypedDict

from react_tk.props.annotations import prop_meta

class A(TypedDict):
    left: Annotated[NotRequired[int], prop_meta(no_value=0, diffing=)]
    right: NotRequired[int]
    top: NotRequired[int]
    bottom: NotRequired[int]
    

class PaddingProps(TypedDict):
    padding: NotRequired[]