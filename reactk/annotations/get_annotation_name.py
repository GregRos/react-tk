from typing import Type

from reactk.annotations.annotation_wrapper import AnnotationWrapper


def get_annotation_name(t: Type):
    """Backward-compatible delegate to the instance-based AnnotationWrapper."""
    return AnnotationWrapper(t).name
