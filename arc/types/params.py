"""Public API for hanlding paramater modification"""
from __future__ import annotations
import typing as t
from arc._command import param


class ParamInfo:
    def __init__(
        self,
        param_cls: type[param.Param] = None,
        arg_alias: str = None,
        short: str = None,
        default: t.Any = param.MISSING,
        description: str = None,
        callback: t.Callable = None,
    ):
        self.param_cls = param_cls
        self.arg_alias = arg_alias
        self.short = short
        self.default = default
        self.description = description
        self.callback = callback

    def dict(self):
        """Used to pass to `Param()` as **kwargs"""
        return {
            "arg_alias": self.arg_alias,
            "short": self.short,
            "default": self.default,
            "description": self.description,
            "callback": self.callback,
        }


def Param(
    *,
    name: str = None,
    short: str = None,
    default: t.Any = param.MISSING,
    description: str = None,
    callback: t.Callable = None,
) -> t.Any:
    """A CLI Paramater. Automatically decides whether it is
    a `positional`, `keyword`, or `flag` paramater.

    # Example
    ```py
    @cli.command()
    def test(val: int = Param(), *, val2: int = Param(), flag: bool = Param()):
        print(val, val2, flag)
    ```
    Each Param type will be determined as follows:
    - `val`: Precedes the bare `*`.
    - `val2`: Proceeds the bare `*`. Python considers this a "keyword only"
        argument, and so does arc
    - `flag`: Has a `bool` type

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
    default: t.Any = param.MISSING,
    description: str = None,
    callback: t.Callable = None,
) -> t.Any:
    """A CLI Paramater. Input will be passed in positionally.

    # Example
    ```py
    @cli.command()
    def test(val: int = PosParam()):
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
    default: t.Any = param.MISSING,
    description: str = None,
    callback: t.Callable = None,
) -> t.Any:
    """A CLI parameter. Input will be passed in by keyword"""
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
    """A Flag represents a boolean value.

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


def SpecialParam(
    name: str = None,
    short: str = None,
    default: t.Any = param.MISSING,
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
        default: t.Any = param.MISSING,
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


as_pos_param = __cls_deco_factory(param.Argument)
as_keyword_param = __cls_deco_factory(param.Option)
as_flag_param = __cls_deco_factory(param.Flag)
as_special_param = __cls_deco_factory(param.SpecialParam)
