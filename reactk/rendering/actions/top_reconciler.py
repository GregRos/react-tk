from collections import defaultdict
from dataclasses import dataclass, field
from inspect import FrameInfo
import sys
from typing import Any, Callable, ClassVar, Generator, Iterable, Optional

from reactk.model.renderable.node.shadow_node import ShadowNode
from reactk.model.renderable.context import Ctx

from reactk.model.renderable.node.top import TopLevelNode
from reactk.model.renderable.trace import RenderFrame
from reactk.model.renderable.trace import RenderTrace, RenderTraceAccessor
from reactk.rendering.actions.compute import (
    AnyNode,
    ComputeTreeActions,
    ReconcileAction,
)
from reactk.rendering.actions.node_reconciler import ReconcilerBase, ReconcilerAccessor
from reactk.rendering.actions.reconcile_state import (
    PersistentReconcileState,
    RenderedNode,
    TransientReconcileState,
)
from reactk.model.renderable.component import Component


def _with_trace(node: ShadowNode[Any], trace: RenderTrace) -> ShadowNode[Any]:
    return RenderTraceAccessor(node).set(trace) or node


@dataclass
class RootReconciler[Node: ShadowNode[Any] = ShadowNode[Any]]:
    state: PersistentReconcileState = field(
        default_factory=lambda: PersistentReconcileState(existing_resources={})
    )

    def _compute_actions(self, transient_state: TransientReconcileState, root):
        return ComputeTreeActions(transient_state).compute_actions(root)

    def reconcile(self, nodes: tuple[ShadowNode[Any], ...]):
        top_level_fake = TopLevelNode(KIDS=nodes)
        self.state.overwrite(RenderedNode(object(), top_level_fake))
        transient_state = self.state.new_transient()
        actions = [*self._compute_actions(transient_state, top_level_fake)]

        for action in actions:
            Reconciler = ReconcilerAccessor(action.node).get()
            reconciler = Reconciler.create(transient_state)
            if not reconciler:
                raise ValueError(
                    f"No reconciler found for action type {type(action.node)}"
                )
            reconciler.run_action(action)
