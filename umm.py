from typing import Any, TypeVar, Generic

T = TypeVar("T")
A = TypeVar("A", bound=Any)


class Example(Generic[T]):
    pass


paramed = Example[int]
print(A)
