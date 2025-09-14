import builtins
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from reactk.model2.ants.generic_reader import Reader_BoundTypeVar
from reactk.model2.util.core_reflection import none_match_ref

if TYPE_CHECKING:
    from reactk.model2.util.type_hints import type_reference


@dataclass
class Reflector:
    inspect_up_to: "type_reference | tuple[type_reference, ...]" = field(default=object)
    localns: Mapping[str, object] = field(default_factory=dict)
    is_supported: Callable[[type], bool] = field(
        init=False, repr=False, hash=False, compare=False
    )

    def __post_init__(self) -> None:
        inspect_up_to = (
            self.inspect_up_to
            if isinstance(self.inspect_up_to, tuple)
            else (self.inspect_up_to,)
        )
        self.is_supported = none_match_ref(*inspect_up_to)

    def type(self, target: type):
        from reactk.model2.ants.readers import Reader_Class

        return Reader_Class(target=target, reflector=self)

    def annotation(self, target: object):
        from reactk.model2.ants.readers import Reader_Annotation

        return Reader_Annotation(target=target, reflector=self)

    def get_type_hints(
        self, cls: builtins.type, **defaults: builtins.type
    ) -> dict[str, object]:
        from reactk.model2.util.type_hints import get_type_hints_up_to

        inspect_up_to = (
            self.inspect_up_to
            if isinstance(self.inspect_up_to, tuple)
            else (self.inspect_up_to,)
        )
        return get_type_hints_up_to(cls, inspect_up_to, **defaults, **self.localns)

    def method(self, target: Callable[..., Any]):
        from reactk.model2.ants.readers import Reader_Method

        return Reader_Method(target=target, reflector=self)

    def generic(self, target: Any):
        """Create a Reader_Generic for the given target using this reflector."""
        from reactk.model2.ants.generic_reader import Reader_Generic

        return Reader_Generic(target=target, reflector=self)

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
