from __future__ import annotations

import typing as t

import arc.typing as at
from arc import errors

if t.TYPE_CHECKING:
    from arc.define.param.param_definition import ParamDefinition

T = t.TypeVar("T", bound=type)


def _default_init(inst: object, **kwargs: t.Any) -> None:
    for key, value in kwargs.items():
        setattr(inst, key, value)


def _default_repr(inst: object) -> str:
    values = ", ".join(
        [
            f"{member}={repr(getattr(inst, member))}"
            for member in inst.__signature__.parameters.keys()  # type: ignore
        ]
    )
    return f"{type(inst).__name__}({values})"


def _default_enter(inst: object) -> object:
    if hasattr(inst, "pre_exec"):
        inst.pre_exec()

    return inst


def _default_exit(inst: object, *args: t.Any) -> object:
    if hasattr(inst, "post_exec"):
        inst.post_exec()

    return inst


_default_group_methods = {
    "__init__": _default_init,
    "__repr__": _default_repr,
    "__enter__": _default_enter,
    "__exit__": _default_exit,
}

_default_group_options: at.ParamGroupOptions = {"exclude": []}


def modify_group_cls(cls: T, options: dict[str, t.Any]) -> T:
    setattr(cls, "__arc_group__", options)
    for name, func in _default_group_methods.items():
        if getattr(cls, name, None) is getattr(object, name, None):
            setattr(cls, name, func)

    return cls


@t.overload
def group(
    cls: None = None, *, exclude: t.Sequence[str] | None = None
) -> t.Callable[[T], T]:
    ...


@t.overload
def group(cls: T) -> T:
    ...


def group(
    cls: T = None, *, exclude: t.Sequence[str] | None = None, **kwargs: t.Any
) -> T | t.Callable[[T], T]:
    """Construct a Parameter group.

    Args:
        cls (T, optional): The class to make into a parameter group
        exclude (t.Sequence[str] | None, optional): List of type to exclude
            from the parameter list. Useful if you assign values to the class
            instance at runtime, but still want to annotate them in your type
            hints


    Returns:
        type: The modified class

    Example:
    ```py
    import arc

    @arc.group
    class MyGroup():
        name: str

    @arc.command
    def command(group: MyGroup):
        print(group.name)

    command("Sean")
    ```
    """

    if cls:
        return modify_group_cls(cls, t.cast(dict[str, t.Any], _default_group_options))

    def inner(cls: T) -> T:
        return modify_group_cls(cls, {"exclude": exclude or [], **kwargs})

    return inner


def isgroup(cls: type) -> bool:
    """Returns a boolean whether or not
    a given type is an arc parameter group"""
    return hasattr(cls, "__arc_group__")


def groupoptions(cls: type) -> dict[str, t.Any]:
    """Returns a dictionary representing the options passed
    in when a parameter group was created. Should be used
    in conjuction with [`isgroup()`][arc.define.param.groups.isgroup].

    Args:
        cls (type): Parameter Group Class

    Raises:
        TypeError: If the passed in type is not a parameter group

    Returns:
        dict[str, t.Any]: The options dictionary
    """
    if not isgroup(cls):
        raise TypeError(f"{cls} is not a parameter group")

    return getattr(cls, "__arc_group__")


def get_cached_definition(cls: type) -> ParamDefinition | None:
    return getattr(cls, "__arc_cached_group_def__", None)


def cache_definition(cls: type, definition: ParamDefinition) -> None:
    setattr(cls, "__arc_cached_group_def__", definition)
