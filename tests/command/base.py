from unittest import TestCase
from typing import Type, List, Dict
from arc.command import Command
from ..mock import mock_command

# pylint: disable=unused-variable, unused-argument
class BaseCommandTest(TestCase):
    command_class: Type[Command]

    def setUp(self):
        self.command = mock_command(cls=self.command_class)

        @self.command.subcommand()
        def no_args():
            ...

        @self.command.subcommand()
        def has_args1(val1: str, val2: int):
            ...

        @self.command.subcommand()
        def has_args2(val1: list, val2: float):
            ...

        @self.command.subcommand()
        def has_args3(val1: bytes, val2: List[int]):
            ...

        @self.command.subcommand()
        def has_flags(flag: bool):
            ...
