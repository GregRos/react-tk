from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Literal, Self

import funcy


from reactk.model2.ants.generic_reader import is_bound, is_not_bound
from reactk.model2.prop_ants import shadow_reflector
from reactk.model2.prop_model import Prop_Schema, Prop_Mapping
from reactk.model.shadow_node import ShadowNode
from reactk.model2.prop_model.common import KeyedValues
from reactk.model2.prop_model.prop import Prop_ComputedMapping

type Compat = Literal["update", "replace", "recreate"]


class Resource[Node: ShadowNode](ABC):
    resource: Any
    type ThisResource = Resource[Node]

    def __repr__(self) -> str:
        return self.node.__repr__()

    @classmethod
    def node_type(cls) -> type[Node]:
        base_annotations = shadow_reflector.type(cls).base_annotations
        fst = funcy.first(base_annotations)
        assert fst is not None and fst.origin is not None
        if not fst.origin.inner_equals(Resource):
            raise TypeError(f"{cls} must directly extend Resource")
        bound_arg = fst.generic[0]
        if is_not_bound(bound_arg):
            raise TypeError(f"{cls} must extend Resource with a bound Node type")
        node_type = bound_arg.value
        return node_type.target

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
    def update(self, props: Prop_ComputedMapping, /) -> None: ...

    @abstractmethod
    def place(self, props: Prop_ComputedMapping, /) -> None: ...

    @abstractmethod
    def unplace(self) -> None: ...

    @abstractmethod
    def replace(self, other: "ThisResource", diff: Prop_ComputedMapping, /) -> None: ...

    @abstractmethod
    def get_compatibility(self, other: Node) -> Compat: ...
