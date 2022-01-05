import pytest
from arc.autocompletions import get_completions
from arc import CLI, Param

from tests import utils


class TestCLI:
    def test_cli_commands(self, cli: CLI):
        @cli.command()
        def command():
            ...

        @command.subcommand()
        def sub():
            ...

        @cli.command()
        def command2():
            ...

        @cli.command()
        def command3():
            ...

        cli("--autocomplete")
