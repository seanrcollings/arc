from arc import utils

from .command import Command
from .keyword_command import KeywordCommand
from .positional_command import PositionalCommand
from .raw_command import RawCommand
from .command_type import CommandType, command_factory
from .context import Context
from .__option import Option


def namespace(
    name: str, function=None, command_type=CommandType.KEYWORD, **kwargs
) -> Command:
    """Creates a Command namespace.

    :param name: name of the namespace / command
    :param function: optional function to be used
        when calling the namespace directly, defaults to no_op
    :param command_type: Type of the command, defaults to KEYWORD
    :param context: dict of context values to be used in this namespace and below
    """
    function = function or utils.no_op
    command = command_factory(name, function, command_type, **kwargs)
    command.__autoload__ = True
    return command
