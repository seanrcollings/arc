"""This module contains various functions that get exposed to the external interface.
They could be placed along with the stuff they interact with, but this felt more convenient"""
from __future__ import annotations
import builtins
import sys
import typing as t
from arc import errors
from arc.color import colorize, fg
from arc.define.command import Command, namespace_callback
from arc.runtime import ExecMiddleware
from arc.present import Joiner, Ansi
from arc.types.type_info import TypeInfo
from arc.types.helpers import convert_type
from arc import utils
import arc.typing as at


def convert(value: str, type: type):
    info = TypeInfo.analyze(type)
    converted = convert_type(info.resolved_type, value, info)

    for middleware in info.middleware:
        converted = utils.dispatch_args(middleware, converted, None)

    return converted


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
        command = Command(
            callback=callback,
            name=Command.get_command_name(callback, name)[0],
            description=desc,
            parent=None,
            explicit_name=bool(name),
            autoload=True,
        )
        command.use(ExecMiddleware.all())
        return command

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
    command = Command(
        callback=namespace_callback,
        name=name,
        description=desc,
        parent=None,
        autoload=True,
    )
    command.use(ExecMiddleware.all())
    return command


def exit(code: int = 0, message: str | None = None) -> t.NoReturn:
    """Exits the application with `code`.
    Optionally recieves a `message` that will be written
    to stderr before exiting"""
    raise errors.Exit(code, message)
