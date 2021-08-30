from typing import Union, GenericAlias, Sequence, _AnnotatedAlias  # type: ignore


def is_annotated(annotation) -> bool:
    return isinstance(annotation, _AnnotatedAlias)


def unwrap(annotation) -> type:
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
    cls = unwrap(cls)
    try:
        return issubclass(cls, classes)
    except TypeError:
        return False


def is_alias(alias):
    return isinstance(alias, GenericAlias) or getattr(alias, "__origin__", False)


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


class UnwrapHelper:
    @classmethod
    def is_origin(cls, other: type):
        other = unwrap(other)
        return cls is other