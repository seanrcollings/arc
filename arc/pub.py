"""This module contains various functions that get exposed to the external interface.
They could be placed along with the stuff they interact with, but this felt more convenient"""
from __future__ import annotations
import builtins
import sys
import typing as t
from arc.context import Context
from arc.core.command import Command, namespace_callback
from arc.types.type_info import TypeInfo
from arc.types.helpers import convert_type
from arc.errors import ArcError
from arc import utils
import arc.typing as at


def convert(value: str, type: type, context: Context | None = None):
    try:
        context = context or Context.current()
    except ArcError:
        context = None

    info = TypeInfo.analyze(type)
    converted = convert_type(info.resolved_type, value, info, context)  # type: ignore

    for middleware in info.middleware:
        converted = utils.dispatch_args(middleware, converted, context, None)

    return converted


def print(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    file: t.IO | None = None,
    flush: bool = False
):
    """A wrapper around `print()` that handles removing escape
    codes when the output is not a TTY"""
    file = file or sys.stdout

    if file and not file.isatty():
        values = tuple(utils.ansi_clean(str(v)) for v in values)

    builtins.print(*values, sep=sep, end=end, file=file, flush=flush)


def exit(code: int = 0, ctx: Context | None = None) -> t.NoReturn:
    """Exits the application with `code`"""
    ctx = ctx or Context.current()
    ctx.exit(code)


def command(
    name: str | None = None, desc: str | None = None
) -> t.Callable[[at.CommandCallback], Command]:
    """Create an arc Command

    ```py
    @arc.command()
    def command():
        print("Hello there!")
    ```

    Args:
        name (str | None, optional): The name for this command.
            If one is not provided, the function's name will be used.
        desc (str | None, optional): Description for the command. If
            one is not provided, the docstring description will be used
    """

    def inner(callback: at.CommandCallback) -> Command:
        return Command(
            callback=callback,
            name=Command.get_command_name(callback, name)[0],
            description=desc,
            parent=None,
            explicit_name=bool(name),
            autoload=True,
        )

    return inner


def namespace(name: str, desc: str | None = None) -> Command:
    """Create an arc Command, that is not executable on it's own,
    but can have commands nested underneath it.

    ```py
    ns = arc.namespace("ns")

    @ns.subcommand()
    def sub():
        print("I'm a subcommand")
    ```

    Args:
        name (str): Name of the command
        desc (str | None, optional): Description for the command.

    Returns:
        command: A command object without a callback associated with it
    """
    return Command(
        callback=namespace_callback,
        name=name,
        description=desc,
        parent=None,
        autoload=True,
    )
