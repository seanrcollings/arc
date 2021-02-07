from .command import Command
from .keyword_command import KeywordCommand
from .positional_command import PositionalCommand
from .raw_command import RawCommand
from .command_type import CommandType, command_factory


def group(name: str, command_type=CommandType.KEYWORD):
    """Creates a Command Group"""
    return command_factory(name, lambda: ..., command_type)
