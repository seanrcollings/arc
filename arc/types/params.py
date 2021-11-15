"""Public API for hanlding paramater modification"""
from __future__ import annotations
from typing import Any, TypeVar
from arc.command import param


class ParamInfo:
    def __init__(
        self,
        param_cls: type[param.Param] = None,
        name: str = None,
        short: str = None,
        default: Any = param.MISSING,
    ):
        self.param_cls = param_cls
        self.name = name
        self.short = short
        self.default = default


def Param(
    name: str = None,
    short: str = None,
    default: Any = param.MISSING,
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
    return ParamInfo(None, name, short, default)


def PosParam(
    name: str = None,
    short: str = None,
    default: Any = param.MISSING,
) -> Any:
    """A CLI Paramater. Input will be passed in positionally.

    # Example
    ```py
    @cli.command()
    def test(val: int = PosParam()):
        print(val)
    ```

    ```
    $ python example.py command 2
    2
    ```
    """
    return ParamInfo(param.PositionalParam, name, short, default)


def KeyParam(
    name: str = None,
    short: str = None,
    default: Any = param.MISSING,
) -> Any:
    """A CLI parameter. Input will be passed in by keyword"""
    return ParamInfo(param.KeywordParam, name, short, default)


def FlagParam(
    name: str = None,
    short: str = None,
    default: Any = param.MISSING,
) -> Any:
    """A CLI parameter. Input will be passed in by
    keyword, but a value is not neccessary"""
    return ParamInfo(param.FlagParam, name, short, default)


def SpecialParam(
    name: str = None,
    short: str = None,
    default: Any = param.MISSING,
) -> Any:
    """Special Params do not select a value from user input.
    As such, they're values must originate elsewhere, or be manually selected.
    """
    return ParamInfo(param.SpecialParam, name, short, default)


T = TypeVar("T")


def __cls_deco_factory(param_cls: type[param.Param]):
    def decorator(
        name: str = None,
        short: str = None,
        default: Any = param.MISSING,
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
                    "overwrite": overwrite,
                },
            )
            return cls

        return inner

    return decorator


as_pos_param = __cls_deco_factory(param.PositionalParam)
as_keyword_param = __cls_deco_factory(param.KeywordParam)
as_flag_param = __cls_deco_factory(param.FlagParam)
as_special_param = __cls_deco_factory(param.SpecialParam)
