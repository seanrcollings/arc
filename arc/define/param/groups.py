from __future__ import annotations
import typing as t
from arc import errors
import arc.typing as at
from arc.define.classful import lazy_class_signature

if t.TYPE_CHECKING:
    from arc.define.param.param_definition import ParamDefinition

T = t.TypeVar("T", bound=type)


def _default_init(inst: object, **kwargs):
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


_default_group_methods = {
    "__init__": _default_init,
    "__repr__": _default_repr,
}

_default_group_options: at.ParamGroupOptions = {"exclude": []}


def modify_group_cls(cls: T, options: at.ParamGroupOptions) -> T:
    setattr(cls, "__arc_group__", options)
    for name, func in _default_group_methods.items():
        if getattr(cls, name) is getattr(object, name):
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


def group(cls: T = None, *, exclude: t.Sequence[str] | None = None):
    """Construct a Parameter group

    ## Example
    ```py
    import arc

    @arc.group
    class MyGroup():
        name: str

    @arc.command()
    def command(group: MyGroup):
        print(group.name)

    command("Sean")
    ```

    """
    if cls:
        return modify_group_cls(cls, _default_group_options)

    def inner(cls: T):
        return modify_group_cls(cls, {"exclude": exclude or []})

    return inner


def isgroup(cls: type) -> bool:
    """Returns a boolean about
    whether or not a given type is an arc parameter group"""
    return hasattr(cls, "__arc_group__")


def groupoptions(cls: type) -> at.ParamGroupOptions:
    """Returns a dictionary representing the options passed
    in when a parameter group was created"""
    if not hasattr(cls, "__arc_group__"):
        raise errors.ParamError(f"{cls} is not a parameter group")

    return getattr(cls, "__arc_group__")


def get_cached_definition(cls: type) -> ParamDefinition | None:
    return getattr(cls, "__arc_cached_group_def__", None)


def cache_definition(cls: type, definition: ParamDefinition) -> None:
    setattr(cls, "__arc_cached_group_def__", definition)
