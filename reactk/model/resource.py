from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Literal, Self

import funcy


from reactk.model2.ants.generic_reader import is_bound, is_not_bound
from reactk.model2.prop_ants import shadow_reflector
from reactk.model2.prop_model import Prop_Schema, Prop_Mapping
from reactk.model.shadow_node import ShadowNode
from reactk.model2.prop_model.common import KeyedValues
from reactk.model2.prop_model.prop import Prop_ComputedMapping
from reactk.rendering.generate_actions import AnyNode

type Compat = Literal["update", "replace", "recreate"]
