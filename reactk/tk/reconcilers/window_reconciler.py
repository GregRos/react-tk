import logging
import threading
from tkinter import Tk
from typing import Any
from reactk.model.shadow_node import ShadowNode
from reactk.model2.prop_model.prop import Prop_ComputedMapping
from reactk.rendering.future_actions import (
    Create,
    Recreate,
    Replace,
    RenderedNode,
    Unplace,
    Update,
    Place,
)
from reactk.rendering.generate_actions import ReconcileAction
from reactk.rendering.reconciler import Reconciler
from reactk.rendering.ui_state import RenderState
from reactk.tk.types.geometry import Geometry
from reactk.tk.reconcilers.widget_reconciler import WidgetReconciler
from reactk.tk.nodes.window import Window

logger = logging.getLogger("ui").getChild("diff")


class WindowReconciler(Reconciler[Tk]):
    def __init__(
        self,
        state: RenderState,
    ):
        self.state = state

    def _normalize_geo(self, existing: Tk, geo: Geometry) -> str:
        x, y, width, height = (geo[k] for k in ("x", "y", "width", "height"))
        if x < 0:
            x = existing.winfo_screenwidth() + x
        if y < 0:
            y = existing.winfo_screenheight() + y
        match geo["anchor_point"]:
            case "lt":
                pass
            case "rt":
                x -= width
            case "lb":
                y -= height
            case "rb":
                x -= width
                y -= height

        return f"{width}x{height}+{x}+{y}"

    def _place(self, pair: RenderedNode[Tk], diff: Prop_ComputedMapping) -> None:
        geo = diff.values["Geometry"]  # type: Geometry
        resource = pair.resource
        normed = self._normalize_geo(resource, geo)
        print(f"Setting {pair.node.to_string_marker("log")} geometry to {normed}")
        resource.wm_geometry(normed)
        resource.deiconify()

    def _replace(self, existing: Tk, replacement: Tk) -> None:
        self._unplace(existing)
        replacement.deiconify()

    def _update(self, resource: Tk, props: Prop_ComputedMapping) -> None:
        if attrs := props.values.get("attributes"):
            attributes = [item for k, v in attrs.items() for item in (f"-{k}", v) if v]
            resource.attributes(*attributes)
        if configure := props.values.get("configure"):
            resource.configure(**configure)
        if (override_redirect := props.values.get("override_redirect")) is not None:
            resource.overrideredirect(override_redirect)

    def _unplace(self, resource: Tk) -> None:
        resource.withdraw()

    def _create(self, node: ShadowNode[Any]) -> "RenderedNode[Tk]":
        waiter = threading.Event()
        tk: Tk = None  # type: ignore

        def ui_thread():
            nonlocal tk
            tk = Tk()
            waiter.set()
            tk.mainloop()

        thread = threading.Thread(target=ui_thread)
        thread.start()
        waiter.wait()

        return RenderedNode(tk, node)

    def _do_create_action(self, action: Update[Tk] | Create[Tk]):
        match action:
            case Create(next, container) as c:
                new_resource = self._create(next)
                self.state.existing_resources[next.uid] = new_resource
                return new_resource
            case Update(existing, next, diff):
                if diff:
                    self._update(existing.resource, diff)
                return existing.migrate(next)
            case _:
                assert False, f"Unknown action: {action}"

    def _run_action_main_thread(self, action: ReconcileAction[Tk]) -> None:
        if action:
            # FIXME: This should be an externalized event
            logger.info(f"⚖️  RECONCILE {action}")
        else:
            logger.info(f"🚫 RECONCILE {action.key} ")
            return

        match action:
            case Update(existing, next, diff):
                self._update(existing.resource, diff)
            case Unplace(existing):
                self._unplace(existing.resource)
            case Place(_, at, Recreate(old, next, container)) as x:
                new_resource = self._do_create_action(Create(next, container))
                old.resource.destroy()
                self._place(new_resource, x.diff)
            case Place(container, at, createAction) as x if not isinstance(
                createAction, Recreate
            ):
                cur = self._do_create_action(createAction)
                self._place(cur, x.diff)
            case Replace(_, existing, Recreate(old, next, container)) as x:
                cur = self._do_create_action(Create(next, container))
                self._replace(existing.resource, cur.resource)
                old.resource.destroy()
            case Replace(container, existing, createAction) if not isinstance(
                createAction, Recreate
            ):
                cur = self._do_create_action(createAction)
                self._update(existing.resource, createAction.diff)
                self._replace(cur.resource, existing.resource)
            case _:
                assert False, f"Unknown action: {action}"
