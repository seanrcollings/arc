from unittest.mock import patch
from unittest import TestCase
from arc.errors import CommandError
from arc import CLI, run

from .mock import mock_command


class TestGroup(TestCase):
    def setUp(self):
        self.group = mock_command("group")
        self.cli = mock_command("cli", CLI)

        self.cli.install_command(self.group)

        @self.group.subcommand()
        def func1(x):
            ...

        @self.group.subcommand()
        def func2(x: int):
            ...

        @self.group.subcommand()
        def func3(x: bool):
            ...

    def test_register(self):
        self.assertIn(self.group.name, self.cli.subcommands.keys())

    def test_run_alone(self):
        run(self.group, "func2 x=2")
        self.group.subcommands["func2"].function.assert_called_with(x=2)

    def test_func1(self):
        self.cli("group:func1 x=2")
        self.cli.subcommands["group"].subcommands["func1"].function.assert_called_with(
            x="2"
        )

    def test_func2(self):
        self.cli("group:func2 x=4")
        self.cli.subcommands["group"].subcommands["func2"].function.assert_called_with(
            x=4
        )

    @patch("arc.utils.handle")
    def test_nonexistant_script(self, _):
        with self.assertRaises(CommandError):
            self.cli("doesnotexist")

    def test_present_flags(self):
        self.cli("group:func3 --x")
        self.cli.subcommands["group"].subcommands["func3"].function.assert_called_with(
            x=True
        )

    def test_absent_flags(self):
        self.cli("group:func3")
        self.cli.subcommands["group"].subcommands["func3"].function.assert_called_with(
            x=False
        )
