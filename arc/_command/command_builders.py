from __future__ import annotations
from typing import Callable

from arc import logging
from arc.color import colorize, fg

from arc._command.command import Command
from arc.context import Context

logger = logging.getArcLogger("build")


def helper(ctx: Context):
    logger.error("%s is not executable.", colorize(ctx.fullname, fg.YELLOW))
    print(ctx.command.get_help(ctx))
    ctx.exit(1)


def namespace(name: str, **kwargs) -> Command:
    """Creates a non-executable Command namespace.

    Namespaces are autoloadable with `cli.autoload()`

    Args:
        name: name of the namespace / command
        state: dict of context values to be used in this namespace and below

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
    c = Command(helper, name, **kwargs)
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

    @command()
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
