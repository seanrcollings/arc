"""Public API for hanlding parameter modification"""
from __future__ import annotations
import typing as t
from arc._command import param
from arc import constants


class ParamInfo:
    def __init__(
        self,
        param_cls: type[param.Param] = None,
        arg_alias: str = None,
        short: str = None,
        default: t.Any = constants.MISSING,
        description: str = None,
        callback: t.Callable = None,
        action: param.ParamAction = None,
    ):
        self.param_cls = param_cls
        self.arg_alias = arg_alias
        self.short = short
        self.default = default
        self.description = description
        self.callback = callback
        self.action = action

    def dict(self):
        """Used to pass to `Param()` as **kwargs"""
        return {
            "arg_alias": self.arg_alias,
            "short": self.short,
            "default": self.default,
            "description": self.description,
            "callback": self.callback,
            "action": self.action,
        }


def Param(
    *,
    name: str = None,
    short: str = None,
    default: t.Any = constants.MISSING,
    description: str = None,
    callback: t.Callable = None,
) -> t.Any:
    """A CLI Paramater. Automatically decides whether it is
    a `positional`, `option` or `flag`

    # Example
    ```py
    @cli.command()
    def test(val: int = Param(), *, val2: int = Param(), flag: bool = Param()):
        print(val, val2, flag)
    ```
    Each Param type will be determined as follows:
    - `val`:  Positional argument because it precedes the bare `*`.
    - `val2`: Option argument because  it proceeds the bare `*`.
              Python considers this a "keyword only" argument, and so does arc
    - `flag`: Flag argument because it has `bool` type

    ```
    $ python example.py test --val2 3 --flag -- 2
    2 3 True
    ```
    """
    return ParamInfo(
        None,
        arg_alias=name,
        short=short,
        default=default,
        description=description,
        callback=callback,
    )


def Argument(
    *,
    name: str = None,
    default: t.Any = constants.MISSING,
    description: str = None,
    callback: t.Callable = None,
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
        param_cls=param.Argument,
        arg_alias=name,
        default=default,
        description=description,
        callback=callback,
    )


def Option(
    *,
    name: str = None,
    short: str = None,
    default: t.Any = constants.MISSING,
    description: str = None,
    callback: t.Callable = None,
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
        param_cls=param.Option,
        arg_alias=name,
        short=short,
        default=default,
        description=description,
        callback=callback,
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
        param_cls=param.Flag,
        arg_alias=name,
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
        param_cls=param.Flag,
        arg_alias=name,
        short=short,
        default=default,
        description=description,
        callback=callback,
        action=param.ParamAction.COUNT,
    )


def SpecialParam(
    name: str = None,
    short: str = None,
    default: t.Any = constants.MISSING,
    description: str = None,
    callback: t.Callable = None,
) -> t.Any:
    """Params marked as "Special" are not exposed to the command line
    interface and cannot recieve user input. As such, they're values
    are expected to come from elsewhere. This allows commands to recieve
    their values like regular params, but still have them act in a particular
    way.

    It is primarly used for some builtin-types like `State` and `Context`.
    """
    return ParamInfo(
        param_cls=param.SpecialParam,
        arg_alias=name,
        short=short,
        default=default,
        description=description,
        callback=callback,
    )


T = t.TypeVar("T")


def __cls_deco_factory(param_cls: type[param.Param]):
    def decorator(
        name: str = None,
        short: str = None,
        default: t.Any = constants.MISSING,
        description: str = None,
        overwrite: bool = False,
    ):
        def inner(cls: T) -> T:
            setattr(
                cls,
                "__param_info__",
                {
                    "param_cls": param_cls,
                    "arg_alias": name,
                    "short": short,
                    "default": default,
                    "description": description,
                    "overwrite": overwrite,
                },
            )
            return cls

        return inner

    return decorator


argument = __cls_deco_factory(param.Argument)
option = __cls_deco_factory(param.Option)
flag = __cls_deco_factory(param.Flag)
special = __cls_deco_factory(param.SpecialParam)
