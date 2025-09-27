from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Literal, Self


type Compat = Literal["update", "replace", "recreate"]
