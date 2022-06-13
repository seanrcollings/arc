import typing as t

import inspect

from arc import constants
from arc._command.param import param
from arc.utils import isdunder


class ParamInfo:
    def __init__(
        self,
        param_cls: type[param.Param],
        param_name: str = None,
        short: str = None,
        default: t.Any = constants.MISSING,
        description: str = None,
        callback: t.Callable = None,
        action: param.Action = None,
        prompt: str = None,
        envvar: str = None,
    ):
        self.param_cls = param_cls
        self.param_name = param_name
        self.short_name = short
        self.default = default
        self.description = description
        self.callback = callback
        self.action = action
        self.prompt = prompt
        self.envvar = envvar

    def dict(self):
        """Used to pass to `Param()` as **kwargs"""
        return {
            "param_name": self.param_name,
            "short_name": self.short_name,
            "default": self.default,
            "description": self.description,
            "callback": self.callback,
            "prompt": self.prompt,
            "envvar": self.envvar,
            "action": self.action,
        }


def Argument(
    *,
    name: str = None,
    default: t.Any = constants.MISSING,
    description: str = None,
    callback: t.Callable = None,
    prompt: str = None,
    envvar: str = None,
) -> t.Any:
    """A CLI Paramater. Input will be passed in positionally.

    # Example
    ```py
    @cli.command()
    def test(val: int = Argument()):
        print(val)
    ```

    ```
    $ python example.py test 2
    2
    ```
    """
    return ParamInfo(
        param_cls=param.ArgumentParam,
        param_name=name,
        default=default,
        description=description,
        callback=callback,
        prompt=prompt,
        envvar=envvar,
    )


def Option(
    *,
    name: str = None,
    short: str = None,
    default: t.Any = constants.MISSING,
    description: str = None,
    callback: t.Callable = None,
    prompt: str = None,
    envvar: str = None,
) -> t.Any:
    """A (generally optional) keyword parameter.

      # Example
    ```py
    @cli.command()
    def test(val: int = Option()):
        print(val)
    ```

    ```
    $ python example.py test --val 2
    2
    ```
    """
    return ParamInfo(
        param_cls=param.OptionParam,
        param_name=name,
        short=short,
        default=default,
        description=description,
        callback=callback,
        prompt=prompt,
        envvar=envvar,
    )


def Flag(
    *,
    name: str = None,
    short: str = None,
    default: bool = False,
    description: str = None,
    callback: t.Callable = None,
) -> t.Any:
    """An option that represents a boolean value.

    # Example
    ```py
    @cli.command()
    def test(val: bool = Flag()):
        print(val)
    ```

    ```
    $ python example.py test
    False
    $ python example.py test --flag
    True
    ```
    """
    return ParamInfo(
        param_cls=param.FlagParam,
        param_name=name,
        short=short,
        default=default,
        description=description,
        callback=callback,
    )


def Count(
    *,
    name: str = None,
    short: str = None,
    default: int = 0,
    description: str = None,
    callback: t.Callable = None,
) -> t.Any:
    """A Flag that counts it's number of apperances on the command line

    # Example
    ```py
    @cli.command()
    def test(val: int = Count(short="v")):
        print(val)
    ```

    ```
    $ python example.py test
    0
    $ python example.py test --val
    1
    $ python example.py test -vvvv
    4
    ```
    """
    return ParamInfo(
        param_cls=param.FlagParam,
        param_name=name,
        short=short,
        default=default,
        description=description,
        callback=callback,
        action=param.Action.COUNT,
    )


def class_signature(cls: type):
    annotations = t.get_type_hints(cls, include_extras=True)
    defaults = {name: getattr(cls, name) for name in dir(cls) if not isdunder(name)}
    attrs = {}

    for name, annotation in annotations.items():
        attrs[name] = (annotation, inspect.Parameter.empty)

    for name, default in defaults.items():
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


def lazy_class_signature(cls: type):
    setattr(cls, "__signature__", classmethod(property(class_signature)))  # type: ignore
    return cls


G = t.TypeVar("G", bound=type)


def group(cls: G) -> G:
    setattr(cls, "__arc_group__", True)
    lazy_class_signature(cls)
    return cls


def Depends(callback: t.Callable) -> t.Any:
    return ParamInfo(param_cls=param.InjectedParam, callback=callback)
