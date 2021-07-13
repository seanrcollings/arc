from typing import _GenericAlias as GenericAlias, _SpecialForm as SpecialForm  # type: ignore
from typing import Union, Literal
from pathlib import Path


def unwrap_type(annotation) -> type:
    """Handles unwrapping `GenericTypes`, `SpecialForms`, etc...
    To retrive the inner origin type.

    For Example:

    - `list[int] -> list`
    - `Union[int, str] -> Union`
    - `File[File.Read] -> File`
    - `list -> list`
    """
    if origin := getattr(annotation, "__origin__", None):
        return origin
    else:
        return annotation


def safe_issubclass(cls, classes: Union[type, tuple[type, ...]]) -> bool:
    """Safe wrapper around issubclass for
    generic types like Union
    """
    cls = unwrap_type(cls)
    try:
        return issubclass(cls, classes)
    except TypeError:
        return False


def is_alias(alias):
    return isinstance(alias, GenericAlias) or getattr(alias, "__origin__", False)


simple_types = {
    str: "string",
    int: "integer",
    float: "decimal",
    bool: "flag",
    Path: "filepath",
}

or_types = {Union, Literal}


def readable_type_name(kind: Union[type, SpecialForm]) -> str:
    unwrapped = unwrap_type(kind)
    if unwrapped in simple_types:
        return simple_types[unwrapped]

    if unwrapped in or_types:
        return (
            ", ".join(simple_types.get(arg) for arg in kind.__args__[:-1])  # type: ignore
            + f" or {simple_types.get(kind.__args__[-1])}"  # type: ignore
        )

    return str(kind)
