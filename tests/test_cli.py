from unittest import TestCase, mock
from pathlib import Path

from arc import CLI, namespace, CommandType
from arc.errors import CommandError
from arc.utilities.debug import debug

from .mock import mock_command


class TestCLI(TestCase):
    def setUp(self):
        self.cli = mock_command("cli", CLI)

        @self.cli.base(command_type=CommandType.KEYWORD)
        def base(val: int):
            ...

        @self.cli.subcommand()
        def func1(x):
            ...

        @self.cli.subcommand()
        @self.cli.subcommand("func2copy")
        def func2(x: int):
            ...

    def test_base(self):
        self.cli("val=2")
        self.cli.default_action.function.assert_called_with(val=2)

    def test_install_group(self):
        g1 = namespace("g1")
        self.cli.install_command(g1)
        self.assertIn(g1, self.cli.subcommands.values())

        g2 = namespace("g2")
        self.cli.install_command(g2)
        self.assertIn(g2, self.cli.subcommands.values())

    def test_execute(self):
        self.cli("func1 x=2")
        self.cli.subcommands["func1"].function.assert_called_with(x="2")

        self.cli("func2 x=2")
        self.cli.subcommands["func2"].function.assert_called_with(x=2)

    def test_multi_name(self):
        self.cli("func2copy x=2")
        self.cli.subcommands["func2copy"].function.assert_called_with(x=2)

    @mock.patch("arc.utils.handle")
    def test_nonexistant_command(self, _):
        with self.assertRaises(CommandError):
            self.cli("doesnotexist x=2")

    def test_autoload_file(self):
        self.cli.autoload(  # type: ignore
            str(Path(__file__).parent.parent / "src/arc/utilities/debug.py")
        )
        self.assertIn("debug", self.cli.subcommands)

    def test_autoload_dir(self):
        self.cli.autoload(  # type: ignore
            str(Path(__file__).parent.parent / "src/arc/utilities")
        )
        self.assertIn("debug", self.cli.subcommands)
        self.assertIn("files", self.cli.subcommands)
        self.assertIn("https", self.cli.subcommands)

    def test_autoload_error(self):
        self.cli.install_command(debug)
        with self.assertRaises(CommandError):
            self.cli.autoload(  # type: ignore
                str(Path(__file__).parent.parent / "src/arc/utilities/debug.py")
            )
