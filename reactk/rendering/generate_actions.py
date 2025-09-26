from dataclasses import dataclass
import logging
from sre_constants import ANY
from typing import (
    Any,
    Iterable,
)

from reactk.model.component import Component
from reactk.rendering.ui_state import RenderState

from .future_actions import (
    Create,
    Recreate,
    Replace,
    RenderedNode,
    Unplace,
    Update,
    Place,
)
from ..model import ShadowNode


from itertools import groupby, zip_longest

logger = logging.getLogger("ui").getChild("diff")
type AnyNode = ShadowNode[ShadowNode[Any]]
type ReconcileAction[Res] = Place[Res] | Replace[Res] | Unplace[Res] | Update[Res]


@dataclass
class _ComputeAction:
    prev: RenderedNode | None
    next: RenderedNode | ShadowNode | None
    container: AnyNode
    at: int

    @property
    def next_node(self) -> AnyNode:
        assert self.next, "next is None"
        return self.next if isinstance(self.next, ShadowNode) else self.next.node  # type: ignore

    @property
    def next_resource(self) -> RenderedNode | None:
        if not self.next or isinstance(self.next, ShadowNode):
            return None
        return self.next

    def _get_inner_action(self):
        assert self.next
        if not self.prev:
            return Create(self.next_node, self.container)
        if self.prev.node.get_compatibility(self.next_node) == "recreate":
            return Recreate(self.prev.resource, self.next_node, self.container)
        return Update(
            self.prev,
            self.next_node,
            diff=self.prev.node.__PROP_VALUES__.diff(self.next_node.__PROP_VALUES__),
        )

    def compute(self):
        if not self.next:
            assert self.prev, "Neither prev nor next exists"
            return Unplace(self.prev, self.container)
        inner_action = self._get_inner_action()
        if not self.prev:
            return Place(
                self.container,
                self.at,
                inner_action,
            )
        if self.prev.node.uid != self.next_node.uid:
            return Replace(self.container, self.prev, inner_action)
        match self.prev.node.get_compatibility(self.next_node):
            case "update" if isinstance(inner_action, Update):
                return inner_action
            case "replace":
                return Replace(self.container, self.prev, inner_action)
            case "recreate":
                return Replace(self.container, self.prev, inner_action)
            case compat:
                raise ValueError(f"Unknown compatibility: {compat}")


@dataclass
class ComputeTreeActions:
    state: RenderState

    @staticmethod
    def _check_duplicates(rendering: Iterable[ShadowNode]):
        key_to_nodes = {
            key: list(group) for key, group in groupby(rendering, key=lambda x: x.uid)
        }
        messages = {
            key: f"Duplicates for {key} found: {group} "
            for key, group in key_to_nodes.items()
            if len(group) > 1
        }
        if messages:
            raise ValueError(messages)

    def _existing_children(self, parent: AnyNode) -> Iterable[RenderedNode]:
        existing_parent = self.state.existing_resources.get(parent.uid)
        if not existing_parent:
            return
        for child in existing_parent.node.__CHILDREN__:
            if child.uid not in self.state.placed:
                existing_child = self.state.existing_resources.get(child.uid)
                if existing_child:
                    yield existing_child

    def compute_actions(
        self, parent: AnyNode, is_creating_new=False
    ) -> Iterable["ReconcileAction"]:
        self._check_duplicates(parent.__CHILDREN__)
        existing_children = self._existing_children(parent)
        pos = -1
        for prev, next in zip_longest(
            existing_children, parent.__CHILDREN__, fillvalue=None
        ):
            prev = self.state.existing_resources.get(prev.node.uid) if prev else None
            if is_creating_new:
                prev = None
            pos += 1
            if not next and prev and prev.node.uid in self.state.placed:
                continue
            if next:
                self.state.placed.add(next.uid)
            prev_resource = (
                self.state.existing_resources.get(prev.node.uid) if prev else None
            )
            next_resource = (
                self.state.existing_resources.get(next.uid) if next else None
            )
            action = _ComputeAction(
                prev=prev_resource or prev,
                next=next_resource or next,
                at=pos,
                container=parent,
            ).compute()
            yield action
            if next and next.__CHILDREN__:
                yield from self.compute_actions(
                    next,
                    is_creating_new=not action.is_creating_new and not is_creating_new,
                )
