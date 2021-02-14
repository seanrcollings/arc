from arc import utils

from .command import Command
from .keyword_command import KeywordCommand
from .positional_command import PositionalCommand
from .raw_command import RawCommand
from .command_type import CommandType, command_factory
from .context import Context


def namespace(name: str, command_type=CommandType.KEYWORD, **kwargs):
    """Creates a Command Group"""
    return command_factory(name, utils.no_op, command_type, **kwargs)
