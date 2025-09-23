from dataclasses import dataclass
import logging
from sre_constants import ANY
from typing import (
    Any,
    Callable,
    Iterable,
)

from .future_actions import (
    Create,
    Recreate,
    Replace,
    Unplace,
    Update,
    Place,
)
from ..model import ShadowNode, Resource


from itertools import groupby, zip_longest

logger = logging.getLogger("ui")
type AnyNode = ShadowNode[ShadowNode[Any]]


@dataclass
class ReconcileTarget:
    prev: Resource | None
    next: Resource | ShadowNode | None
    container: AnyNode
    at: int

    @property
    def next_node(self) -> AnyNode:
        assert self.next, "next is None"
        return self.next if isinstance(self.next, ShadowNode) else self.next.node  # type: ignore

    @property
    def next_resource(self) -> Resource | None:
        if not self.next or isinstance(self.next, ShadowNode):
            return None
        return self.next

    def _get_inner_action(self):
        assert self.next
        if not self.prev:
            return Create(self.next_node)
        if self.prev.get_compatibility(self.next_node) == "recreate":
            return Recreate(self.prev.resource, self.next_node)
        return Update(
            self.prev,
            self.next_node,
            diff=self.prev.node.__PROP_VALUES__.diff(self.next_node.__PROP_VALUES__),
        )

    def get_outer_action(self):
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
        if self.prev.uid != self.next_node.uid:
            return Replace(self.container, self.prev, inner_action)
        match self.prev.get_compatibility(self.next_node):
            case "update":
                return inner_action
            case "replace":
                return Replace(self.container, self.prev, inner_action)
            case "recreate":
                return Replace(self.container, self.prev, inner_action)
            case compat:
                raise ValueError(f"Unknown compatibility: {compat}")


@dataclass
class ReconcileKidsTarget:
    parent: AnyNode
    _existing_resources: dict[str, Resource]
    _placed = set[str]()

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

    def compute_reconcile_actions(self, parent: AnyNode, is_creating_new=False):
        self._check_duplicates(parent.__CHILDREN__)
        parent_resource = self._existing_resources[parent.uid]
        pos = -1
        for prev, next in zip_longest(
            parent_resource.kids, parent.__CHILDREN__, fillvalue=None
        ):
            if is_creating_new:
                prev = None
            pos += 1
            if not next and prev and prev.uid in self._placed:
                continue
            if next:
                self._placed.add(next.uid)
            prev_resource = self._existing_resources.get(prev.uid) if prev else None
            next_resource = self._existing_resources.get(next.uid) if next else None
            action = ReconcileTarget(
                prev=prev_resource or prev,
                next=next_resource or next,
                at=pos,
                container=parent,
            ).get_outer_action()
            if next and next.__CHILDREN__:
                self.compute_reconcile_actions(
                    next,
                    is_creating_new=not action.is_creating_new and not is_creating_new,
                )


class Reconciler:

    type ReconcileAction = Place | Replace | Unplace | Update
    type CreateAction = Create | Recreate | Update
    type ThisResource = Resource
    type Construct = Callable[[AnyNode], ThisResource]
    existing_resources: dict[str, ThisResource]

    def __init__(
        self,
        resource_type: type[ThisResource],
        create: Construct,
    ):
        self._placement = ()
        self.existing_resources = {}
        self.create = create
        self.resource_type = resource_type

    def _do_create_action(self, action: Update | Create):
        match action:
            case Create(next) as c:
                new_resource = self.create(next)  # type: ignore
                new_resource.update(c.diff)
                self.existing_resources[next.uid] = new_resource
                return new_resource
            case Update(existing, next, diff):
                if diff:
                    existing.update(diff)
                return existing.migrate(next)
            case _:
                assert False, f"Unknown action: {action}"

    def _do_reconcile_action(self, action: ReconcileAction, log=True):
        if action:
            # FIXME: This should be an externalized event
            logger.info(f"⚖️  RECONCILE {action}")
        else:
            logger.info(f"🚫 RECONCILE {action.key} ")
            return

        match action:
            case Update(existing, next):
                self._do_create_action(action)
            case Unplace(existing):
                existing.unplace()
            case Place(container, at, Recreate(old, next)) as x:
                existing_container = self.existing_resources[container.uid]
                new_resource = self._do_create_action(Create(next))
                old.destroy()
                new_resource.place(existing_container, x.diff, at)
            case Place(container, at, createAction) as x if not isinstance(
                createAction, Recreate
            ):
                existing_container = self.existing_resources[container.uid]
                resource = self._do_create_action(createAction)
                resource.place(existing_container, x.diff, at)
            case Replace(container, existing, Recreate(old, next)) as x:
                resource = self._do_create_action(Create(next))
                existing.replace(resource, x.diff)
                old.destroy()
            case Replace(container, existing, createAction) if not isinstance(
                createAction, Recreate
            ):
                resource = self._do_create_action(createAction)
                existing.replace(resource, createAction.diff)
            case _:
                assert False, f"Unknown action: {action}"

    def reconcile(self, actions: Iterable[ReconcileAction]):
        for action in actions:
            self._do_reconcile_action(action)
