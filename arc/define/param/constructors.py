import typing as t

import arc.typing as at
from arc import constants
from arc.define.param import param


class ParamInfo:
    def __init__(
        self,
        param_cls: type[param.Param[t.Any]],
        param_name: str = None,
        short: str = None,
        default: t.Any = constants.MISSING,
        desc: str = None,
        callback: at.ParamCallback = None,
        action: param.Action = None,
        prompt: str = None,
        envvar: str = None,
        complete: at.CompletionFunc = None,
        getter_func: at.ParamGetter = None,
        data: dict[str, t.Any] = None,
    ):
        self.param_cls = param_cls
        self.param_name = param_name
        self.short_name = short
        self.default = default
        self.desc = desc
        self.callback = callback
        self.action = action
        self.prompt = prompt
        self.envvar = envvar
        self.complete = complete
        self.getter_func = getter_func
        self.data = data or {}

    def dict(self) -> dict[str, t.Any]:
        """Used to pass to `Param()` as **kwargs"""
        return {
            "param_name": self.param_name,
            "short_name": self.short_name,
            "default": self.default,
            "description": self.desc,
            "callback": self.callback,
            "prompt": self.prompt,
            "envvar": self.envvar,
            "action": self.action,
            "comp_func": self.complete,
            "getter_func": self.getter_func,
            "data": self.data,
        }


def Argument(
    *,
    name: str = None,
    default: t.Any = constants.MISSING,
    desc: str = None,
    callback: at.ParamCallback = None,
    prompt: str = None,
    envvar: str = None,
    get: at.ParamGetter = None,
    complete: at.CompletionFunc = None,
    **kwargs: t.Any,
) -> t.Any:
    """A CLI argument. Input is passed positionally.


    Args:
        name (str, optional): The name to use for the parameter on the command line.
        default (t.Any, optional): A default value for the parameter. If one is given,
            the argument becomes optional, otherwise it is required.
        desc (str, optional): A description of the parameter, will be added to the `--help` doc.
        callback (t.Callable, optional): a Callable object that can be used to modify the value of this parameter.
        prompt (str, optional): A string to provide the user with as a prompt to request input
            from STDIN when none is provided from the command line.
        envvar (str, optional): Name of an enviroment variable to obtain a value from if one is not
            provided on the command line.
        get (at.GetterFunc, optional): Callable object to retrive a possible value for the command if one
            is not provided on the command line.
        complete (at.CompletionFunc, optional): Function to provide shell completions for this parameter.

    ## Example
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
        desc=desc,
        callback=callback,
        prompt=prompt,
        envvar=envvar,
        getter_func=get,
        complete=complete,
        data=kwargs,
    )


def Option(
    *,
    name: str = None,
    short: str = None,
    default: t.Any = constants.MISSING,
    desc: str = None,
    callback: at.ParamCallback = None,
    prompt: str = None,
    envvar: str = None,
    get: at.ParamGetter = None,
    complete: at.CompletionFunc = None,
    **kwargs: t.Any,
) -> t.Any:
    """A (generally optional) keyword parameter.

    Args:
        name (str, optional): The name to use for the parameter on the command line.
        short (str, optional): A single character name to refer to this parameter to on the command line (`--name` vs `-n`)
        default (t.Any, optional): A default value for the parameter. If one is given,
            the argument becomes optional, otherwise it is required.
        desc (str, optional): A description of the parameter, will be added to the `--help` doc.
        callback (t.Callable, optional): a Callable object that can be used to modify the value of this parameter.
        prompt (str, optional): A string to provide the user with as a prompt to request input
            from STDIN when none is provided from the command line.
        envvar (str, optional): Name of an enviroment variable to obtain a value from if one is not
            provided on the command line.
        get (at.GetterFunc, optional): Callable object to retrive a possible value for the command if one
            is not provided on the command line.
        complete (at.CompletionFunc, optional): Function to provide shell completions for this parameter.

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
        desc=desc,
        callback=callback,
        prompt=prompt,
        envvar=envvar,
        getter_func=get,
        complete=complete,
        data=kwargs,
    )


def Flag(
    *,
    name: str = None,
    short: str = None,
    default: bool = False,
    desc: str = None,
    callback: at.ParamCallback = None,
    **kwargs: t.Any,
) -> t.Any:
    """An option that represents a boolean value.

    Args:
        name (str, optional): The name to use for the parameter on the command line.
        short (str, optional): A single character name to refer to this parameter to on the command line (`--name` vs `-n`)
        default (boolean, optional): A default value for the parameter. If one is given,
            the argument becomes optional, otherwise it is required.
        desc (str, optional): A description of the parameter, will be added to the `--help` doc.
        callback (t.Callable, optional): a Callable object that can be used to modify the value of this parameter.

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
        desc=desc,
        callback=callback,
        data=kwargs,
    )


def Count(
    *,
    name: str = None,
    short: str = None,
    default: int = 0,
    desc: str = None,
    callback: at.ParamCallback = None,
    **kwargs: t.Any,
) -> t.Any:
    """A Flag that counts it's number of apperances on the command line

    Args:
        name (str, optional): The name to use for the parameter on the command line.
        short (str, optional): A single character name to refer to this parameter to on the command line (`--name` vs `-n`)
        default (int, optional): The starting point for the counter. Should be an integer.
        desc (str, optional): A description of the parameter, will be added to the `--help` doc.
        callback (t.Callable, optional): a Callable object that can be used to modify the value of this parameter.

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
        desc=desc,
        callback=callback,
        action=param.Action.COUNT,
        data=kwargs,
    )


def Depends(callback: at.ParamCallback, **kwargs: t.Any) -> t.Any:
    return ParamInfo(param_cls=param.InjectedParam, callback=callback, data=kwargs)
