from unittest import TestCase, mock
from pathlib import Path
import pytest

from arc import CLI, namespace, ParsingMethod
from arc.errors import CommandError
from arc.builtin.debug import debug


def test_base(cli: CLI):
    @cli.default()
    def base(val: int):
        return val

    assert cli("val=2") == 2


def test_install_group(cli: CLI):
    g1 = namespace("g1")
    cli.install_command(g1)
    assert g1 in cli.subcommands.values()

    g2 = namespace("g2")
    cli.install_command(g2)
    assert g2 in cli.subcommands.values()


def test_execute(cli: CLI):
    cli("func1 x=2")
    cli("func2 x=2")


def test_nonexistant_command(cli: CLI):
    with pytest.raises(CommandError), mock.patch("arc.utils.handle"):
        cli("doesnotexist x=2")


class TestAutoload:
    root = Path(__file__).parent.parent

    def test_autoload_file(self, cli: CLI):
        cli.autoload(str(self.root / "arc/builtin/debug.py"))
        assert "debug" in cli.subcommands

    def test_autoload_dir(self, cli: CLI):
        cli.autoload(str(self.root / "arc/builtin"))
        assert "debug" in cli.subcommands
        assert "files" in cli.subcommands
        assert "https" in cli.subcommands

    def test_autoload_error(self, cli: CLI):
        cli.install_command(debug)
        with pytest.raises(CommandError):
            cli.autoload(str(self.root / "arc/builtin/debug.py"))


def test_command_alias(cli: CLI):
    @cli.subcommand(("name1", "name2"))
    def name1():
        return True

    assert cli("name2")


def test_keybab(cli: CLI):
    @cli.subcommand()
    def two_words(first_name):
        return True

    assert cli("two_words first_name=sean")
    assert cli("two-words first-name=sean")


def test_positional(cli: CLI):
    @cli.subcommand(parsing_method=ParsingMethod.POSITIONAL)
    def pos(val: int):
        return True

    assert cli("pos 2")
