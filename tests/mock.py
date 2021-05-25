from __future__ import annotations
from typing import Dict, Type
from unittest.mock import MagicMock, create_autospec

from arc.command import Command, CommandType, KeywordCommand
from arc.cli import CLI


class MockedCommand(Command):
    function: MagicMock
    subcommands: Dict[str, MockedCommand]  # type: ignore

    def create_command(self, name, function, command_type=None, **kwargs):
        cls = CommandType.command_type_mappings.get(command_type) or type(self).mro()[2]
        if cls is CLI:
            cls = KeywordCommand

        return mock_command(name, cls, function, **kwargs)


def mock_command(
    name: str = "mock", cls: Type[Command] = KeywordCommand, func=lambda: ..., **kwargs
) -> MockedCommand:
    mocked = type(f"Mocked{cls.__name__}", (MockedCommand, cls), {})
    if hasattr(func, "mock"):
        mocked_func = func
    else:
        mocked_func = create_autospec(func)
        mocked_func.__annotations__ = func.__annotations__
    return mocked(name, mocked_func, **kwargs)
