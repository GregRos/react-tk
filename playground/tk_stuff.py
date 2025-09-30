# pyright: reportUnboundVariable=false
# pyright: basic
from time import sleep
from tkinter import Label, Frame, Tk
from threading import Thread
import functools
import threading
import time
from typing import Any, Callable


# new top-level decorator with type hints
def run_on_tk[X: Callable[..., Any]](fn: X) -> X:
    """
    Ensure the wrapped instance method runs on self._tk via after.
    If self._tk isn't available yet, a background daemon thread polls
    until it is and then schedules the call. The wrapper returns None
    (immediate scheduling).
    """

    @functools.wraps(fn)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> None:
        tkobj = getattr(self, "_tk", None)
        if isinstance(tkobj, Tk):
            tkobj.after(0, lambda: fn(self, *args, **kwargs))
            return None

        def waiter() -> None:
            while True:
                tk2 = getattr(self, "_tk", None)
                if isinstance(tk2, Tk):
                    tk2.after(0, lambda: fn(self, *args, **kwargs))
                    return
                time.sleep(0.01)

        t = threading.Thread(target=waiter, daemon=True)
        t.start()
        return None

    return wrapper  # type: ignore[return]


class Blah:
    _thread: Thread
    _tk: Tk
    _label: Label
    _frame: Frame

    def _start_ui(self):
        self._tk = Tk()
        self._tk.mainloop()

    def __init__(self):
        self._thread = Thread(target=self._start_ui)
        self._thread.start()

    @run_on_tk
    def setup_geo(self):
        # scheduled on the Tk event loop
        self._tk.geometry("400x400")
        self._frame = Frame(self._tk)
        self._label = Label(self._tk, text="Hello, World!")
        self._label.pack(in_=self._frame, ipadx=20, ipady=20)

    @run_on_tk
    def unhide(self):
        self._label.pack(in_=self._tk)


blah = Blah()
blah.setup_geo()
sleep(2)
blah.unhide()
