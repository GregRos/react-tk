from dataclasses import dataclass
import logging
from sre_constants import ANY
from typing import (
    Any,
    Iterable,
)

from react_tk.renderable.component import Component
from react_tk.renderable.node.prop_value_accessor import PropValuesAccessor
from react_tk.props.impl.prop import Prop
from react_tk.rendering.actions.reconcile_state import (
    PersistentReconcileState,
    TransientReconcileState,
)

from .actions import (
    Create,
    Recreate,
    Replace,
    RenderedNode,
    Unplace,
    Update,
    Place,
)
from react_tk.renderable.node.shadow_node import ShadowNode


from itertools import groupby, zip_longest

logger = logging.getLogger("ui").getChild("diff")
type AnyNode = ShadowNode[ShadowNode[Any]]
type ReconcileAction[Res] = Place[Res] | Replace[Res] | Unplace[Res] | Update[Res]


@dataclass
class _ComputeAction:
    prev: RenderedNode | None
    next: ShadowNode | None
    container: AnyNode
    at: int

    @property
    def next_resource(self) -> RenderedNode | None:
        if not self.next or isinstance(self.next, ShadowNode):
            return None
        return self.next

    def _get_compatibility(self, older: RenderedNode, newer: AnyNode) -> str:
        from react_tk.rendering.actions.node_reconciler import ReconcilerAccessor

        reconciler_class = ReconcilerAccessor(older.node).get()
        return reconciler_class.get_compatibility(older, newer)

    def _get_inner_action(self):
        assert self.next
        if not self.prev:
            return Create(self.next, self.container)
        if self._get_compatibility(self.prev, self.next) == "recreate":
            return Recreate(self.prev, self.next, self.container)
        return Update(
            self.prev,
            self.next,
            diff=PropValuesAccessor(self.prev.node)
            .get()
            .diff(PropValuesAccessor(self.next).get()),
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
        if self.prev.node.__uid__ != self.next.__uid__:
            return Replace(self.container, self.prev, inner_action)
        match self._get_compatibility(self.prev, self.next):
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
    state: TransientReconcileState

    @staticmethod
    def _check_duplicates(rendering: Iterable[ShadowNode]):
        key_to_nodes = {
            key: list(group)
            for key, group in groupby(rendering, key=lambda x: x.__uid__)
        }
        messages = {
            key: f"Duplicates for {key} found: {group} "
            for key, group in key_to_nodes.items()
            if len(group) > 1
        }
        if messages:
            raise ValueError(messages)

    def _existing_children(self, parent: AnyNode) -> Iterable[RenderedNode]:
        existing_parent = self.state.existing_resources.get(parent.__uid__)
        if not existing_parent:
            return
        for child in existing_parent.node.KIDS:
            if child.__uid__ not in self.state.placed:
                existing_child = self.state.existing_resources.get(child.__uid__)
                if existing_child:
                    yield existing_child

    def compute_actions(
        self, parent: AnyNode, is_creating_new=False
    ) -> Iterable["ReconcileAction"]:
        self._check_duplicates(parent.KIDS)
        existing_children = self._existing_children(parent)
        pos = -1
        for prev, next in zip_longest(existing_children, parent.KIDS, fillvalue=None):
            prev = (
                self.state.existing_resources.get(prev.node.__uid__) if prev else None
            )
            if is_creating_new:
                prev = None
            pos += 1
            if not next and prev and prev.node.__uid__ in self.state.placed:
                continue
            if next:
                self.state.placed.add(next.__uid__)
            prev_resource = (
                self.state.existing_resources.get(prev.node.__uid__) if prev else None
            )

            action = _ComputeAction(
                prev=prev_resource or prev,
                next=next,
                at=pos,
                container=parent,
            ).compute()
            yield action
            if next and next.KIDS:
                yield from self.compute_actions(
                    next,
                    is_creating_new=action.is_creating_new or is_creating_new,
                )
