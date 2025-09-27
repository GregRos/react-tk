from reactk.model.top import TopLevelNode
from reactk.rendering.generate_actions import ReconcileAction
from reactk.rendering.reconciler import Reconciler


class TopLevelReconciler(Reconciler[object]):

    def run_action(self, action: ReconcileAction[object]) -> None:
        if action.is_creating_new:
            self._register(action.node, object())