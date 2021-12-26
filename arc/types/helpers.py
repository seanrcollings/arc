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
    TYPE_CHECKING,
)
import re

from arc import utils, result

if TYPE_CHECKING:
    from arc.typing import Annotation
    from arc.types.aliases import TypeProtocol
    from arc.context import Context


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
        return (
            self._name
            or getattr(self.origin, "name", None)
            or getattr(self.origin, "__name__", None)
            or str(self.origin)
        )

    def is_optional_type(self) -> bool:
        """The type is `Optional[T]`"""
        return (
            self.origin is Union
            and len(self.sub_types) == 2
            and self.sub_types[-1].base is type(None)
        )

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


def validate(cls):
    """Class decorator to mark a class as validatable.
    On instantiation any method who's name follows
    the form `-?validate.+` will be executed. Note that this
    includes protected methods, but not private ones
    """
    if not hasattr(cls, "__init__"):
        return cls

    cls_init = cls.__init__

    validators = list(
        v
        for n in dir(cls)
        if n.strip("_").startswith("validate") and callable(v := getattr(cls, n))
    )

    def init(instance, *args, **kwargs):
        if cls_init is object.__init__:
            cls_init(instance)
        else:
            cls_init(instance, *args, **kwargs)

        for validator in validators:
            validator(instance)

    cls.__init__ = init

    return cls


def convert(
    protocol: type[TypeProtocol],
    value: Any,
    info: TypeInfo,
    ctx: Context,
):
    """Uses `protocol` to convert `value`"""
    return utils.dispatch_args(protocol.__convert__, value, info, ctx)


def safe_issubclass(typ, classes: Union[type, tuple[type, ...]]) -> bool:
    try:
        return issubclass(typ, classes)
    except TypeError:
        return False


def iscontextmanager(obj: Any) -> bool:
    return hasattr(obj, "__enter__") and hasattr(obj, "__exit__")


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


def match(pattern: str, string: str) -> result.Result[None, str]:
    if not re.match(pattern, string):
        return result.Err(f"does not follow required format: {pattern}")

    return result.Ok()
