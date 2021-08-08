from arc import utils

from .command import Command
from .context import Context
from .argument_parser import ParsingMethod, ArgumentParser, PositionalParser
from .executable import VarKeyword, VarPositional


def namespace(name: str, parsing_method=ParsingMethod.STANDARD, **kwargs) -> Command:
    """Creates a non-executable Command namespace.

    Namespaces are autoloadable with `cli.autoload()`

    Args:
        name: name of the namespace / command
        command_type: Type of the command, defaults to KEYWORD
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
    and `ns` would not be a valid command
    """
    c = Command(name, utils.no_op, parsing_method, **kwargs)
    c.__autoload__ = True  # type: ignore
    return c


def command(name: str = None, parsing_method=ParsingMethod.STANDARD, **kwargs):
    """Creates an executable Command namespace.

    Autoloadable with `cli.autoload()`
    Args:
       name: name of the namespace / command
       command_type: Type of the command, defaults to KEYWORD
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

    def inner(function):
        cmd_name = name or function.__name__
        c = Command(cmd_name, function, parsing_method, **kwargs)
        c.__autoload__ = True  # type: ignore
        return c

    return inner
