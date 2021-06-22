from unittest import TestCase, mock
from pathlib import Path
import pytest

from arc import CLI, namespace
from arc.errors import CommandError
from arc.utilities.debug import debug

from .mock import mock_command, mock_typed_func, MockedCommand


@pytest.fixture
def cli():
    cli = mock_command("cli", CLI)

    def base(val: int):
        ...

    mocked = mock_typed_func(base)
    cli.base()(mocked)

    @cli.subcommand()
    def func1(x):
        ...

    @cli.subcommand()
    @cli.subcommand("func2copy")
    def func2(x: int):
        ...

    return cli


def test_base(cli: MockedCommand):
    cli("val=2")
    cli.default_action.function.assert_called_with(val=2)


def test_install_group(cli: MockedCommand):
    g1 = namespace("g1")
    cli.install_command(g1)
    assert g1 in cli.subcommands.values()

    g2 = namespace("g2")
    cli.install_command(g2)
    assert g2 in cli.subcommands.values()


def test_execute(cli: MockedCommand):
    cli("func1 x=2")
    cli.subcommands["func1"].function.assert_called_with(x="2")

    cli("func2 x=2")
    cli.subcommands["func2"].function.assert_called_with(x=2)


def test_multi_name(cli: MockedCommand):
    cli("func2copy x=2")
    cli.subcommands["func2copy"].function.assert_called_with(x=2)


def test_nonexistant_command(cli: MockedCommand):
    with pytest.raises(CommandError), mock.patch("arc.utils.handle"):
        cli("doesnotexist x=2")


def test_autoload_file(cli: MockedCommand):
    cli.autoload(  # type: ignore
        str(Path(__file__).parent.parent / "src/arc/utilities/debug.py")
    )
    assert "debug" in cli.subcommands


def test_autoload_dir(cli: MockedCommand):
    cli.autoload(  # type: ignore
        str(Path(__file__).parent.parent / "src/arc/utilities")
    )
    assert "debug" in cli.subcommands
    assert "files" in cli.subcommands
    assert "https" in cli.subcommands


def test_autoload_error(cli: MockedCommand):
    cli.install_command(debug)
    with pytest.raises(CommandError):
        cli.autoload(  # type: ignore
            str(Path(__file__).parent.parent / "src/arc/utilities/debug.py")
        )


def test_command_alias(cli: MockedCommand):
    @cli.subcommand(("name1", "name2"))
    def name1():
        ...

    cli("name2")
    name1.function.assert_called_with()


def test_keybab(cli: MockedCommand):
    @cli.subcommand()
    def two_words(first_name):
        ...

    cli("two_words first_name=sean")
    cli("two-words first-name=sean")

    assert two_words.function.call_count == 2
