from typing import Dict, Type
from unittest.mock import MagicMock, create_autospec

from arc.command import Command, CommandType, KeywordCommand


class MockedCommand(Command):
    function: MagicMock
    subcommands: Dict[str, "MockedCommand"]  # type: ignore

    def create_command(self, name, function, command_type=None, **kwargs):
        cls = CommandType.command_type_mappings.get(command_type) or type(self).mro()[2]
        return mock_command(name, cls, function)


def mock_command(
    name: str = "mock", cls: Type[Command] = KeywordCommand, func=lambda: ...
) -> MockedCommand:
    mocked = type(f"Mocked{cls.__name__}", (MockedCommand, cls), {})
    return mocked(name, create_autospec(func))
