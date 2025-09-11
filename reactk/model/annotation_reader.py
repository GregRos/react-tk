from dataclasses import dataclass
from types import MethodType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Iterator,
    Mapping,
    TypeGuard,
    TypedDict,
    get_type_hints,
    overload,
)

from reactk.annotations.annotation_wrapper import AnnotationWrapper
from reactk.annotations.get_methods import get_attrs_downto


if TYPE_CHECKING:
    from reactk.model.props.prop_section import PropSection
    from reactk.model.props.prop_dict import PropDict
    from reactk.model.props.prop import Prop


name = "__reactk_annotations__"


@dataclass
class CustomReader:
    target: object

    @property
    def custom(self) -> Any:
        return getattr(self.target, name, None)

    @custom.setter
    def custom(self, value: Any) -> None:
        setattr(self.target, name, value)


type Func = Callable[..., Any]
type Readable = type | Func


@dataclass
class BaseWrapper:
    target: Readable

    def _assert_callable(self) -> None:
        if not self.is_callable:
            raise TypeError(f"Target {self.target!r} is not callable")

    @property
    def is_callable(self) -> bool:
        return callable(self.target)


@dataclass
class ObjectType(BaseWrapper):
    _annotations: dict[str, type]

    def __post_init__(self):
        if not isinstance(self.target, type):
            raise TypeError(f"Target {self.target!r} is not a type")


class AnnotationReader:
    _annotations: dict[str, type]
    _methods: dict[str, Func]

    @property
    def target(self) -> Readable:
        return self._target

    def __init__(self, target: Readable) -> None:
        if target is None:
            raise ValueError("Target cannot be None")
        self._target = target
        self._refresh_annotations()

    def get_method(self, key: str):
        return AnnotationReader(self._methods[key])                    

    def get_annotation(self, key: str) -> AnnotationWrapper[Any]:
        return AnnotationWrapper(self._annotations.get(key))

    def __setitem__(self, key: str, value: Any) -> None:
        self._target.__annotations__[key] = value
        self._refresh_annotations()

    def _refresh_annotations(self) -> None:
        self._annotations = get_type_hints(
            self._target, include_extras=True, localns={"Node": "object"}
        )``
        if not isinstance(self._target, type):
            self._methods = {}
            return

        for key, val in get_attrs_downto(
            self._target, {object, TypedDict, MethodType}
        ).items():
            if callable(val):
                self._methods[key] = val

    def returns(self) -> AnnotationWrapper[Any] | None:
        self._assert_callable()
        return self.get("return", None)

    def arg(self, pos: int) -> AnnotationWrapper[Any]:
        self._assert_callable()
        try:
            return next(x for i, x in enumerate(self.args) if i == pos)
        except StopIteration:
            raise IndexError(pos) from None

    @property
    def args(self) -> Iterable[AnnotationWrapper[Any]]:
        self._assert_callable()
        for k, v in self.items():
            if k == "return":
                continue
            yield v

    def _assert_callable(self) -> None:
        if not self.is_callable:
            raise TypeError(f"Target {self._target!r} is not callable")

    @property
    def is_callable(self) -> bool:
        return callable(self._target)


def read_class_annotations[Obj: object](target: Obj) -> AnnotationReader[Obj]:
    return AnnotationReader(target)
