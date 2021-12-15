from __future__ import annotations
from typing import Callable

from arc import result, logging
from arc.color import colorize, fg

from arc._command.command import Command

logger = logging.getArcLogger("build")


def no_op(ctx):
    return result.Err(
        f"{colorize(ctx.state.command_name, fg.YELLOW)} is not executable. "
        f"Check {colorize('help ' + ctx.state.command_name, fg.ARC_BLUE)} for subcommands"
    )


def helper(ctx):
    logger.warning("%s is not executable.", colorize(ctx.state.command_name, fg.YELLOW))
    return ctx.state.root(f"help {ctx.state.command_name}")


def namespace(name: str, show_help: bool = True, **kwargs) -> Command:
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
    c = Command(helper if show_help else no_op, name, **kwargs)
    c.__autoload__ = True  # type: ignore
    return c


def command(name: str = "", **kwargs) -> Callable[[Callable], Command]:
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
        # cmd_name = name or function.__name__
        c = Command(function, name, **kwargs)
        c.__autoload__ = True  # type: ignore
        return c

    return inner
