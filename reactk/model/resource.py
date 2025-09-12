from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Literal, Self


from reactk.model2.prop_model import PropSection, PValues
from reactk.model.shadow_node import ShadowNode
from reactk.model2.prop_model.common import KeyedValues

type Compat = Literal["update", "replace", "recreate"]


class Resource[Node: ShadowNode](ABC):
    resource: Any

    def __repr__(self) -> str:
        node_type_name = self.__class__.node_type().__name__
        return self.node.__repr__()

    @staticmethod
    @abstractmethod
    def node_type() -> type[Node]: ...
    @abstractmethod
    def is_same_resource(self, other: Self) -> bool: ...

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, self.__class__)
            and self.node == value.node
            and self.is_same_resource(value)
        )

    def __init__(self, node: Node):
        self.node = node

    @abstractmethod
    def migrate(self, node: Node) -> Self: ...

    @abstractmethod
    def destroy(self) -> None: ...

    @property
    def uid(self) -> str:
        return self.node.uid

    @abstractmethod
    def update(self, props: PValues) -> None: ...

    @abstractmethod
    def place(self) -> None: ...

    @abstractmethod
    def unplace(self) -> None: ...

    @abstractmethod
    def replace(self, other: Self) -> None: ...

    @abstractmethod
    def get_compatibility(self, other: Node) -> Compat: ...
