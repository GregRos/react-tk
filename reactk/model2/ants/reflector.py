from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from reactk.model2.ants.generic_reader import Reader_BoundTypeVar


@dataclass
class Reflector:
    inspect_up_to: type = field(default=object)
    localns: Mapping[str, object] = field(default_factory=dict)

    def type(self, target: type):
        from reactk.model2.ants.readers import Reader_Class

        return Reader_Class(target=target, reflector=self)

    def annotation(self, target: object):
        from reactk.model2.ants.readers import Reader_Annotation

        return Reader_Annotation(target=target, reflector=self)

    def method(self, target: Callable[..., Any]):
        from reactk.model2.ants.readers import Reader_Method

        return Reader_Method(target=target, reflector=self)

    def type_var(self, target: TypeVar, *, is_undeclared=False):
        from reactk.model2.ants.generic_reader import Reader_TypeVar

        return Reader_TypeVar(
            target=target, reflector=self, is_undeclared=is_undeclared
        )

    def type_arg(self, target: TypeVar, value: Any, *, is_undeclared=False):
        from reactk.model2.ants.generic_reader import Reader_BoundTypeVar

        return Reader_BoundTypeVar(
            target=target,
            reflector=self,
            is_undeclared=is_undeclared,
            value=self.annotation(value),
        )
