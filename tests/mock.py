from __future__ import annotations
from typing import Dict, Type
from unittest.mock import MagicMock, create_autospec

from arc.command import Command, ParsingMethod, ArgumentParser


class MockedCommand(Command):
    function: MagicMock
    subcommands: Dict[str, MockedCommand]  # type: ignore

    def __init__(self, name, function, *args, **kwargs):
        if not getattr(function, "mock", None):
            function = mock_typed_func(function)

        super().__init__(name, function, *args, **kwargs)

    def subcommand(self, name=None, parsing_method=None, context=None):  # type: ignore
        """Create and install a subcommand

        Fallback for parsing_method:
          - provided argument
          - type of `self.parser`
        """

        parsing_method = parsing_method or type(self.parser)  # type: ignore
        context = context or {}  # type: ignore

        @self.ensure_function
        def decorator(function):
            command_name = self.handle_command_aliases(name or function.__name__)
            command = MockedCommand(command_name, function, parsing_method, context)
            return self.install_command(command)

        return decorator


def mock_command(
    name: str = "mock",
    cls: Type[Command] = Command,
    parser: Type[ArgumentParser] = ParsingMethod.KEYWORD,
    func=lambda: ...,
    **kwargs,
) -> MockedCommand:
    mocked_cls = type(f"Mocked{cls.__name__}", (MockedCommand, cls), {})
    command = mocked_cls(name, func, parser, **kwargs)
    return command


def mock_typed_func(func):
    mocked = create_autospec(func)
    mocked.__annotations__ = func.__annotations__
    return mocked
