from unittest import mock

from arc import run
from arc.command import KeywordCommand
from arc.errors import CommandError, ValidationError

from .base import BaseCommandTest


class TestKeywordCommand(BaseCommandTest):
    command_class = KeywordCommand

    def test_run(self):
        run(self.command, "no_args")
        self.command.subcommands["no_args"].function.assert_called_with()

        run(self.command, "has_args1 val1=string val2=2")
        self.command.subcommands["has_args1"].function.assert_called_with(
            val1="string", val2=2
        )

        run(self.command, "has_args2 val1=string,string val2=2.6")
        self.command.subcommands["has_args2"].function.assert_called_with(
            val1=["string", "string"], val2=2.6
        )

        run(self.command, "has_args2 val1='string,string', val2=2.6")
        self.command.subcommands["has_args2"].function.assert_called_with(
            val1=["string", "string", ""], val2=2.6
        )

        run(self.command, "has_args3 val1=bytes val2=1,2,3,4")
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
            run(self.command, "has_args1 string 2")

    def test_kebab_case(self):
        @self.command.subcommand()
        def has_kebab(test_value: int, test_flag: bool):
            ...

        run(self.command, "has_kebab test_value=2")
        has_kebab.function.assert_called_with(test_value=2, test_flag=False)

        run(self.command, "has-kebab test-value=2")
        has_kebab.function.assert_called_with(test_value=2, test_flag=False)

        run(self.command, "has-kebab test-value=2 --test_flag")
        has_kebab.function.assert_called_with(test_value=2, test_flag=True)

        run(self.command, "has-kebab test-value=2 --test-flag")
        has_kebab.function.assert_called_with(test_value=2, test_flag=True)
