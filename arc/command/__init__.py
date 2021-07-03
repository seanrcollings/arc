from arc import utils

from .command import Command
from .context import Context
from .argument_parser import ParsingMethod, ArgumentParser, PositionalParser


def namespace(
    name: str, function=None, parsing_method=ParsingMethod.KEYWORD, **kwargs
) -> Command:
    """Creates a Command namespace.

    Namespaces are autoloadable with `cli.autoload()`
    Args:
        name: name of the namespace / command
        function: optional function to be used
            when calling the namespace directly, defaults to no_op
        command_type: Type of the command, defaults to KEYWORD
        context: dict of context values to be used in this namespace and below
    """
    function = function or utils.no_op
    command = Command(name, function, parsing_method, **kwargs)
    command.__autoload__ = True  # type: ignore
    return command
