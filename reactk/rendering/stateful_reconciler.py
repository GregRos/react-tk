import logging
from typing import (
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


class StatefulReconciler[Node: ShadowNode]:

    type ReconcileAction = Place | Replace | Unplace | Update
    type CreateAction = Create | Recreate | Update
    type ThisResource = Resource[Node]
    type Construct = Callable[[Node], ThisResource]
    _placement: tuple[Node, ...]
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

    def _get_reconcile_action(self, prev: Node | None, next: Node | None):

        if not next:
            assert prev, "Neither prev nor next exists"
            record = self._key_to_resource[prev.uid]
            return Unplace(record)

        old_next_placement = self._key_to_resource.get(next.uid)

        if not prev:
            if not old_next_placement:
                return Place(Create(next))
            if old_next_placement.get_compatibility(next) == "recreate":
                return Place(Recreate(old_next_placement, next))
            return Place(
                Update(
                    old_next_placement,
                    next,
                    diff=old_next_placement.node.__PROP_VALUES__.diff(
                        next.__PROP_VALUES__
                    ),
                )
            )

        old_prev_placement = self._key_to_resource[prev.uid]

        if prev.uid != next.uid:
            if not old_next_placement:
                return Replace(old_prev_placement, Create(next))
            if old_next_placement.get_compatibility(next) == "recreate":
                return Replace(old_prev_placement, Recreate(old_next_placement, next))
            return Replace(
                old_prev_placement,
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
            diff=prev.__PROP_VALUES__.diff(next.__PROP_VALUES__),
        )
        match old_prev_placement.get_compatibility(next):
            case "update":
                return upd
            case "replace":
                return Replace(old_prev_placement, upd)
            case "recreate":
                return Replace(old_prev_placement, Recreate(old_next_placement, next))
            case compat:
                raise ValueError(f"Unknown compatibility: {compat}")

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

    def compute_reconcile_actions(self, rendering: Iterable[Node]):
        self._check_duplicates(rendering)
        placed = set[str]()
        for prev, next in zip_longest(self._placement, rendering, fillvalue=None):
            if not next and prev and prev.uid in placed:
                continue
            if next:
                placed.add(next.uid)
            yield self._get_reconcile_action(prev, next)

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
            case Place(Recreate(old, next)) as x:
                new_resource = self._do_create_action(Create(next))
                old.destroy()
                new_resource.place(x.diff)
            case Place(createAction) as x if not isinstance(createAction, Recreate):
                resource = self._do_create_action(createAction)
                resource.place(x.diff)
            case Replace(existing, Recreate(old, next)) as x:
                resource = self._do_create_action(Create(next))
                existing.replace(resource, x.diff)
                old.destroy()
            case Replace(existing, createAction) if not isinstance(
                createAction, Recreate
            ):
                resource = self._do_create_action(createAction)
                existing.replace(resource, createAction.diff)
            case _:
                assert False, f"Unknown action: {action}"

    def reconcile(self, rendering: tuple[Node, ...]):
        reconciles = [*self.compute_reconcile_actions(rendering)]
        for reconcile in reconciles:
            self._do_reconcile_action(reconcile)
        self._placement = rendering
