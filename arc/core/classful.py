import functools
import typing as t
import inspect

from arc.utils import isdunder
import arc.typing as at
from arc import errors


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
