from abc import ABC, abstractmethod
from copy import copy
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    ClassVar,
    Literal,
    NotRequired,
    Self,
    TypedDict,
    override,
)


from reactk.model.props.prop_dict import PropDict
from reactk.model.props.prop_section import PropSection
from reactk.model.annotation_reader import AnnotationReader
from reactk.model.props.prop import Prop
from reactk.model.props.prop_values import (
    PValues,
)

from reactk.model.props.prop_value import PropValue
from reactk.model.trace.render_trace import Display, RenderTrace


class InitPropsBase(TypedDict):
    key: Annotated[NotRequired[str], Prop(no_value=None)]


class ShadowProps(InitPropsBase):
    children: Annotated[NotRequired[tuple[Self, ...]], Prop(no_value=())]
    trace: Annotated[NotRequired[RenderTrace], Prop(no_value=None)]


class ShadowNode:
    _props: PValues

    @property
    def trace(self) -> RenderTrace:
        x = self._props.get("trace")
        assert x, "Trace must exist before calling trace."
        v = x.value
        assert isinstance(v, RenderTrace), "Trace must be RenderTrace object"
        return v

    @classmethod
    def node_name(cls) -> str:
        return cls.__name__

    @property
    def type_name(self) -> str:
        return self.__class__.node_name()

    def __init_subclass__(cls) -> None:
        props = AnnotationReader(cls).section = PropSection(
            recurse=True, name=cls.node_name()
        ).merge_class(cls)
        original_post_init = getattr(cls, "__post_init__", None)

        def init_props(self):
            original_post_init(self) if original_post_init else None
            self.props = props.with_values({})

        setattr(cls, "__post_init__", init_props)

    def __repr__(self) -> str:
        return self._props.__repr__()

    @property
    def key(self) -> str | None:
        x = self._props.get("key")
        assert not isinstance(x, PValues), "Key should not be a PValues."
        return x.value if x else None

    def to_string_marker(self, display: Display) -> str:
        return self.trace.to_string(display)

    @property
    def uid(self) -> str:
        assert self.trace, "Trace must exist before calling u_key."
        return self.trace.to_string("id")

    def _copy(self, **overrides: Any) -> Self:
        clone = copy(self)
        # FIXME: This is a hack that shouldn't exist.
        # trace and key should not be props at all
        clone._props = self._props.merge(overrides)

        return clone
