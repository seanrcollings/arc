from unittest import TestCase, mock

from arc import CLI, group
from arc.errors import CommandError

from .mock import mock_command


class TestCLI(TestCase):
    def setUp(self):
        self.cli = mock_command("cli", CLI)

        @self.cli.subcommand()
        def func1(x):
            ...

        @self.cli.subcommand()
        def func2(x: int):
            ...

    def test_install_group(self):
        g1 = group("g1")
        self.cli.install_command(g1)
        self.assertIn(g1, self.cli.subcommands.values())

        g2 = group("g2")
        self.cli.install_command(g2)
        self.assertIn(g2, self.cli.subcommands.values())

    # def test_execute(self):
    #     self.cli("func1 x=2")
    #     self.cli.subcommands["func1"].function.assert_called_with(x="2")

    #     self.cli("func2 x=2")
    #     self.cli.subcommands["func2"].function.assert_called_with(x=2)

    @mock.patch("arc.utils.handle")
    def test_nonexistant_command(self, _):
        with self.assertRaises(CommandError):
            self.cli("doesnotexist x=2")
