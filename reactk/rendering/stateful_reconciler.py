from dataclasses import dataclass
import logging
from sre_constants import ANY
from typing import (
    Any,
    Callable,
    Iterable,
)

from reactk.rendering.generate_actions import AnyNode

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


@dataclass
class ReconcileTarget:
    prev: Resource | None
    next: AnyNode | None
    old_next_placement: Resource | None
    container: AnyNode

    def get_action(self):
        prev = self.prev
        next = self.next
        container = self.container
        if not next:
            assert prev, "Neither prev nor next exists"
            return Unplace(prev, container)

        old_next_placement = self.old_next_placement

        if not prev:
            if not old_next_placement:
                return Place(
                    container,
                    Create(next),
                )
            if old_next_placement.get_compatibility(next) == "recreate":
                return Place(container, Recreate(old_next_placement, next))
            return Place(
                container,
                Update(
                    old_next_placement,
                    next,
                    diff=old_next_placement.node.__PROP_VALUES__.diff(
                        next.__PROP_VALUES__
                    ),
                ),
            )

        if prev.uid != next.uid:
            if not old_next_placement:
                return Replace(container, prev, Create(next))
            if old_next_placement.get_compatibility(next) == "recreate":
                return Replace(container, prev, Recreate(old_next_placement, next))
            return Replace(
                container,
                prev,
                Update(
                    old_next_placement,
                    next,
                    diff=old_next_placement.node.__PROP_VALUES__.diff(
                        next.__PROP_VALUES__
                    ),
                ),
            )

        assert old_next_placement
        upd = Update(
            old_next_placement,
            next,
            diff=prev.node.__PROP_VALUES__.diff(next.__PROP_VALUES__),
        )
        match prev.get_compatibility(next):
            case "update":
                return upd
            case "replace":
                return Replace(container, prev, upd)
            case "recreate":
                return Replace(container, prev, Recreate(old_next_placement, next))
            case compat:
                raise ValueError(f"Unknown compatibility: {compat}")


class StatefulReconciler:

    type ReconcileAction = Place | Replace | Unplace | Update
    type CreateAction = Create | Recreate | Update
    type ThisResource = Resource
    type Construct = Callable[[AnyNode], ThisResource]
    _placement: tuple[AnyNode, ...]
    _key_to_resource: dict[str, ThisResource]

    def __init__(
        self,
        resource_type: type[ThisResource],
        create: Construct,
    ):
        self._placement = ()
        self._key_to_resource = {}
        self.create = create
        self.resource_type = resource_type

    @property
    def node_type(self) -> type[ShadowNode]:
        return self.resource_type.node_type()

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

    def compute_reconcile_actions(self, parent: AnyNode, rendering: Iterable[AnyNode]):
        self._check_duplicates(rendering)
        placed = set[str]()
        resource = self._key_to_resource[parent.uid]
        for prev, next in zip_longest(resource.kids, rendering, fillvalue=None):
            if not next and prev and prev.uid in placed:
                # already placed, skip
                continue
            if next:
                placed.add(next.uid)
            yield ReconcileTarget(
                prev=self._key_to_resource.get(prev.uid) if prev else None,
                next=next,
                old_next_placement=(
                    self._key_to_resource.get(next.uid) if next else None
                ),
                container=parent,
            ).get_action()

    def _do_create_action(self, action: Update | Create):
        match action:
            case Create(next) as c:
                new_resource = self.create(next)  # type: ignore
                new_resource.update(c.diff)
                self._key_to_resource[next.uid] = new_resource
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
            case Place(container, Recreate(old, next)) as x:
                new_resource = self._do_create_action(Create(next))
                old.destroy()
                new_resource.place(x.diff)
            case Place(container, createAction) as x if not isinstance(
                createAction, Recreate
            ):
                resource = self._do_create_action(createAction)
                resource.place(x.diff)
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

    def reconcile(self, rendering: tuple[AnyNode, ...]):
        reconciles = [*self.compute_reconcile_actions(rendering)]
        for reconcile in reconciles:
            self._do_reconcile_action(reconcile)
        self._placement = rendering
