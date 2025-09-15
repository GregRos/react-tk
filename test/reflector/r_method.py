import pytest

from reactk.model2.ants.reflector import Reflector


def func_with_annotations(a: int, b: str) -> int:
    return 0


def func_without_return(a: int, b: str):
    return 0


class RMethod_Test:
    r: Reflector = Reflector()

    def it_has_name_and_debug_signature(self):
        m = self.r.method(func_with_annotations)
        assert m.name == "func_with_annotations"
        # debug signature should include the function name, annotated args and return
        assert m._debug_signature.startswith("func_with_annotations(")
        assert "-> int" in m._debug_signature

    def it_preserves_target(self):
        m = self.r.method(func_with_annotations)
        # Reader_Method.__post_init__ sets target to the original function if no
        # __reactk_original__ accessor is present; that should be the same object.
        assert m.target is func_with_annotations

    def it_checks_arg_index_bounds(self):
        m = self.r.method(func_with_annotations)
        assert m.arg(0) == self.r.annotation(int)
        assert m.arg(1) == self.r.annotation(str)

        with pytest.raises(IndexError):
            m.arg(2)

    def it_handles_returns_and_missing_return_annotation(self):
        m = self.r.method(func_with_annotations)
        assert m.returns() == self.r.annotation(int)

        with pytest.raises(KeyError):
            self.r.method(func_without_return).returns()
