import inspect
import typing as t


def class_signature(cls: type) -> inspect.Signature:
    """Constructs a `inspect.Signature` object for a type.
    It uses the class-level annotations as the parameters so
    that we can treat the classes and functions the same
    """
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


def lazy_class_signature(cls: type) -> type:
    setattr(cls, "__signature__", classmethod(property(class_signature)))  # type: ignore
    return cls


def isdunder(string: str, double_dunder: bool = False) -> bool:
    if double_dunder:
        return string.startswith("__") and string.endswith("__")

    return string.startswith("__")
