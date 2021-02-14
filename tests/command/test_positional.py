from unittest import mock
from arc import run
from arc.command import PositionalCommand
from arc.errors import CommandError, ValidationError

from .base import BaseCommandTest


class TestPositionalCommand(BaseCommandTest):
    command_class = PositionalCommand

    def test_run(self):
        run(self.command, "no_args")
        self.command.subcommands["no_args"].function.assert_called_with()

        run(self.command, "has_args1 string 2")
        self.command.subcommands["has_args1"].function.assert_called_with(
            val1="string", val2=2
        )

        run(self.command, "has_args2 string,string 2.6")
        self.command.subcommands["has_args2"].function.assert_called_with(
            val1=["string", "string"], val2=2.6
        )

        run(self.command, "has_args2 'string,string' 2.6")
        self.command.subcommands["has_args2"].function.assert_called_with(
            val1=["string", "string"], val2=2.6
        )

        run(self.command, "has_args3 bytes 1,2,3,4")
        self.command.subcommands["has_args3"].function.assert_called_with(
            val1=b"bytes", val2=[1, 2, 3, 4]
        )

        run(self.command, "has_flags")
        self.command.subcommands["has_flags"].function.assert_called_with(flag=False)

        run(self.command, "has_flags --flag")
        self.command.subcommands["has_flags"].function.assert_called_with(flag=True)

    @mock.patch("arc.utils.handle")
    def test_error(self, _):
        with self.assertRaises(CommandError):
            run(self.command, "doesnotexist")

        with self.assertRaises(ValidationError):
            run(self.command, "has_args1 val=string")
