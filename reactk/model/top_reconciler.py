from reactk.model.top import TopLevelNode
from reactk.rendering.generate_actions import ReconcileAction
from reactk.rendering.reconciler import Reconciler


class TopLevelReconciler(Reconciler[TopLevelNode]):
    def run_action(self, action: ReconcileAction[TopLevelNode]) -> None:
        pass
