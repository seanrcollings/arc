import typing as t
import builtins


def issubclass(typ: t.Any, classes: type | tuple[type, ...]) -> bool:
    try:
        return builtins.issubclass(typ, classes)
    except TypeError:
        return False


def isinstance(obj: object, classes: type | tuple[type, ...]) -> bool:
    try:
        return builtins.isinstance(obj, classes)
    except TypeError:
        return False
