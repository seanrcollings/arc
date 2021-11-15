from __future__ import annotations
from typing import Callable

from arc.color import colorize, fg
from arc.types import Context
from arc import result
from arc.config import config
from arc.command.command import Command


def no_op(ctx: Context):
    namespace_str = config.namespace_sep.join(ctx.state.command_namespace)

    return result.Err(
        f"{colorize(namespace_str, fg.YELLOW)} is not executable. "
        f"Check {colorize('help ' + namespace_str, fg.ARC_BLUE)} for subcommands"
    )


def namespace(name: str, **kwargs) -> Command:
    """Creates a non-executable Command namespace.

    Namespaces are autoloadable with `cli.autoload()`

    Args:
        name: name of the namespace / command
        context: dict of context values to be used in this namespace and below

    Usage:
    ```py
    from arc import namespace

    ns = namespace("ns")

    @ns.subcommand()
    def hello():
        print('Hi there')
    ```
    When installed into a CLI, the function could be executed with `ns:hello`
    but `ns` would not be a valid command
    """
    c = Command(name, no_op, **kwargs)
    c.__autoload__ = True  # type: ignore
    return c


def command(name: str = None, **kwargs) -> Callable[[Callable], Command]:
    """Creates an executable Command namespace.

    Autoloadable with `cli.autoload()`

    Args:
       name: name of the namespace / command
       context: dict of context values to be used in this namespace and below

    Usage:
    ```py
    from arc import command

    @command
    def hello():
        print('Hi there')
    ```
    When installed into a CLI, the function could be executed with `hello`
    """

    def inner(function: Callable):
        cmd_name = name or function.__name__
        c = Command(cmd_name, function, **kwargs)
        c.__autoload__ = True  # type: ignore
        return c

    return inner
