from typing import Sequence, Union


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


def safe_issubclass(_type: type, _classes: Union[type, tuple[type, ...]]):
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
