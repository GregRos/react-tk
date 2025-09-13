"""Standalone test for _get_own_type_hints behavior.

This script defines the helper and checks that it only evaluates annotations
declared on the inspected class (does not resolve inherited annotations).

Run with the project's python interpreter.
"""

from typing import get_type_hints
import sys
from types import SimpleNamespace


# --- Test cases --------------------------------------------------------------


class A:
    # Should NOT be evaluated when inspecting subclasses
    bad_attribute: "NonExistentType"


class B(A):
    b_attr: int


class C(B):
    c_attr: "Node"


class D(C):
    d_attr: "A"  # refers to base class name explicitly


if __name__ == "__main__":
    # C should only expose its own annotation 'c_attr' (Node resolved to object)
    hints_C = _get_own_type_hints(C)
    print("hints_C:", hints_C)
    assert (
        "c_attr" in hints_C
        and "b_attr" not in hints_C
        and "bad_attribute" not in hints_C
    )
    assert hints_C["c_attr"] is object

    # B should not include bad_attribute, but will include b_attr
    hints_B = _get_own_type_hints(B)
    print("hints_B:", hints_B)
    assert "b_attr" in hints_B and "bad_attribute" not in hints_B

    # D references A by name; since we limit resolution to D's class dict + module, "A" should resolve
    # from the module globals (A is defined in the module) and therefore be evaluated.
    hints_D = _get_own_type_hints(D)
    print("hints_D:", hints_D)
    assert hints_D["d_attr"] is A

    print("All assertions passed.")
