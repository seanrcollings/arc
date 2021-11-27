from __future__ import annotations
from dataclasses import dataclass
from typing import (
    Optional,
    Sequence,
    Union,
    Any,
    get_origin,
    Annotated,
    get_args,
    Generic,
    TypeVar,
)
import re

from arc.typing import Annotation


T = TypeVar("T")


@dataclass
class TypeInfo(Generic[T]):
    base: Annotation
    origin: type[T]
    sub_types: tuple[TypeInfo, ...]
    annotations: tuple[Any, ...]
    _name: Optional[str] = None

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        elif name := getattr(self.origin, "name", None):
            return name
        elif name := getattr(self.origin, "__name__", None):
            return name

        return str(self.origin)

    @classmethod
    def analyze(cls, annotation) -> TypeInfo:
        base = annotation
        origin = get_origin(annotation) or annotation
        annotated_args: tuple = tuple()

        if origin is Annotated:
            args = get_args(annotation)
            annotation = args[0]
            origin = get_origin(annotation) or annotation
            annotated_args = args[1:]

        sub_types = tuple(cls.analyze(arg) for arg in get_args(annotation))

        return cls(
            base=base,
            origin=origin,
            sub_types=sub_types,
            annotations=annotated_args,
        )


def isclassmethod(method):
    bound_to = getattr(method, "__self__", None)

    if not isinstance(bound_to, type):
        return False

    name = method.__name__
    for cls in bound_to.__mro__:
        descriptor = vars(cls).get(name)
        if descriptor is not None:
            return isinstance(descriptor, classmethod)

    return False


def safe_issubclass(_type, _classes: Union[type, tuple[type, ...]]):
    try:
        return issubclass(_type, _classes)
    except TypeError:
        return False


def joiner(values: Sequence, join_str: str = ", ", last_str: str = ", "):
    """Joins values together with an additional `last_str` to format how
    the final value is joined to the rest of the list

    Args:
        values (Sequence): Values to join
        join_str (str, optional): What to join values 0 - penultimate value with. Defaults to ", ".
        last_str (str, optional): [description]. What to use to join the last
            value to the rest. Defaults to ", ".
    """
    if len(values) == 1:
        return values[0]

    return join_str.join(str(v) for v in values[:-1]) + last_str + str(values[-1])


def join_or(values: Sequence) -> str:
    """Joins a Sequence of items with commas
    and an or at the end

    [1, 2, 3, 4] -> "1, 2, 3 or 4"

    Args:
        values (Sequence): Values to join

    Returns:
        str: joined values
    """
    return joiner(values, last_str=" or ")


def join_and(values: Sequence) -> str:
    """Joins a Sequence of items with commas
    and an "and" at the end

    Args:
        values (Sequence): Values to join

    Returns:
        str: joined values
    """
    return joiner(values, last_str=" and ")


def match(pattern: str, string: str):
    if not re.match(pattern, string):
        raise ValueError(f"does not follow required format: {pattern}")
