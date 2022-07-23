import typing as t

from arc import constants
from arc._command.classful import lazy_class_signature
from arc._command.param import param
import arc.typing as at


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
        complete: at.CompletionFunc = None,
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
        self.complete = complete

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
            "comp_func": self.complete,
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
        arc.print(val)
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
    complete: at.CompletionFunc = None,
) -> t.Any:
    """A (generally optional) keyword parameter.

    # Example
    ```py
    @cli.command()
    def test(val: int = Option()):
        arc.print(val)
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
        complete=complete,
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
        arc.print(val)
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
        arc.print(val)
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


def Depends(callback: t.Callable) -> t.Any:
    return ParamInfo(param_cls=param.InjectedParam, callback=callback)


G = t.TypeVar("G", bound=type)


def group(cls: G) -> G:
    setattr(cls, "__arc_group__", True)
    lazy_class_signature(cls)
    return cls
