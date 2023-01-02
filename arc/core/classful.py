import functools
import typing as t
import inspect

import arc.typing as at
from arc import errors


def isdunder(string: str, double_dunder: bool = False):
    if double_dunder:
        return string.startswith("__") and string.endswith("__")

    return string.startswith("__")


def wrap_class_callback(cls: type[at.ClassCallback]):
    if not hasattr(cls, "handle"):
        raise errors.CommandError("class-style commands require a handle() method")

    def wrapper(**kwargs):
        inst = cls()
        for key, value in kwargs.items():
            setattr(inst, key, value)

        return cls.handle(inst)

    class_signature(cls)
    functools.update_wrapper(wrapper, cls)
    return wrapper


def lazy_class_signature(cls: type):
    setattr(cls, "__signature__", classmethod(property(class_signature)))  # type: ignore
    return cls


def class_signature(cls: type):
    annotations = t.get_type_hints(cls, include_extras=True)
    defaults = {name: getattr(cls, name) for name in dir(cls) if not isdunder(name)}
    attrs = {}

    for name, annotation in annotations.items():
        attrs[name] = (annotation, inspect.Parameter.empty)

    for name, default in defaults.items():
        if inspect.isfunction(default):
            continue

        if name in attrs:
            attrs[name] = (attrs[name][0], default)
        else:
            attrs[name] = (t.Any, default)

    parameters = [
        inspect.Parameter(
            name=name,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=default,
            annotation=annotation,
        )
        for name, (annotation, default) in attrs.items()
    ]

    sig = inspect.Signature(
        sorted(parameters, key=lambda p: not p.default is inspect.Parameter.empty)
    )
    # inspect.signature() checks for a cached signature object
    # at __signature__. So we can cache it there
    # to generate the correct signature object
    # during the parameter building process
    setattr(cls, "__signature__", sig)
    return sig


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


default_group_methods = {
    "__init__": _default_init,
    "__repr__": _default_repr,
}


def modify_group_cls(cls: T) -> T:
    setattr(cls, "__arc_group__", True)
    for name, func in default_group_methods.items():
        if getattr(cls, name) is getattr(object, name):
            setattr(cls, name, func)

    lazy_class_signature(cls)
    return cls
