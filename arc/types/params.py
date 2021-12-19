"""Public API for hanlding paramater modification"""
from __future__ import annotations
from typing import Any, TypeVar
from arc._command import param


class ParamInfo:
    def __init__(
        self,
        param_cls: type[param.Param] = None,
        name: str = None,
        short: str = None,
        default: Any = param.MISSING,
        description: str = None,
    ):
        self.param_cls = param_cls
        self.name = name
        self.short = short
        self.default = default
        self.description = description


def Param(
    name: str = None,
    short: str = None,
    default: Any = param.MISSING,
    description: str = None,
) -> Any:
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
    return ParamInfo(None, name, short, default, description)


def Argument(
    name: str = None,
    default: Any = param.MISSING,
    description: str = None,
) -> Any:
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
        name=name,
        default=default,
        description=description,
    )


def Option(
    name: str = None,
    short: str = None,
    default: Any = param.MISSING,
    description: str = None,
) -> Any:
    """A CLI parameter. Input will be passed in by keyword"""
    return ParamInfo(
        param_cls=param.Option,
        name=name,
        short=short,
        default=default,
        description=description,
    )


def Flag(
    name: str = None,
    short: str = None,
    default: bool = False,
    description: str = None,
) -> Any:
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
        name=name,
        short=short,
        default=default,
        description=description,
    )


def SpecialParam(
    name: str = None,
    short: str = None,
    default: Any = param.MISSING,
    description: str = None,
) -> Any:
    """Params marked as "Special" are not exposed to the command line
    interface and cannot recieve user input. As such, they're values
    are expected to come from elsewhere. This allows commands to recieve
    their values like regular params, but still have them act in a particular
    way.

    It is primarly used for some builtin-types like `State` and `Context`.
    """
    return ParamInfo(
        param_cls=param.SpecialParam,
        name=name,
        short=short,
        default=default,
        description=description,
    )


T = TypeVar("T")


def __cls_deco_factory(param_cls: type[param.Param]):
    def decorator(
        name: str = None,
        short: str = None,
        default: Any = param.MISSING,
        description: str = None,
        overwrite: bool = False,
    ):
        def inner(cls: T) -> T:
            setattr(
                cls,
                "__param_info__",
                {
                    "param_cls": param_cls,
                    "name": name,
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
