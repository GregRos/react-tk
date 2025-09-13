from typing import Annotated, Any, TypeVar, Generic

T = TypeVar("T")
A = TypeVar("A", bound=Any)


print(Annotated[int, 1].__args__)
