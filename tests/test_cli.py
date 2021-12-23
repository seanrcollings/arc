from unittest import mock
from pathlib import Path
import pytest

from arc import CLI, namespace, errors
from arc.errors import CommandError
from arc._debug import debug


def test_install_group(cli: CLI):
    g1 = namespace("g1")
    cli.install_command(g1)
    assert g1 in cli.subcommands.values()

    g2 = namespace("g2")
    cli.install_command(g2)
    assert g2 in cli.subcommands.values()


def test_execute(cli: CLI):
    @cli.subcommand()
    def func1(x):
        assert isinstance(x, str)
        return x

    @cli.subcommand()
    @cli.subcommand("func2copy")
    def func2(x: int):
        assert isinstance(x, int)
        return x

    cli("func1 2")
    cli("func2 2")


def test_nonexistant_command(cli: CLI):
    with pytest.raises(errors.CommandNotFound):
        cli("doesnotexist x=2")


class TestAutoload:
    root = Path(__file__).parent.parent

    def test_autoload_file(self, cli: CLI):
        cli.subcommands.pop("debug")
        cli.autoload(str(self.root / "arc/_debug.py"))
        assert "debug" in cli.subcommands

    # def test_autoload_dir(self, cli: CLI):
    #     cli.autoload(str(self.root / "arc/builtin"))
    #     assert "debug" in cli.subcommands
    #     assert "files" in cli.subcommands
    #     assert "https" in cli.subcommands

    def test_autoload_error(self, cli: CLI):
        with pytest.raises(CommandError):
            cli.autoload(str(self.root / "arc/_debug.py"))


def test_command_alias(cli: CLI):
    @cli.subcommand(("name1", "name2"))
    def name1():
        return True

    assert cli("name2")
