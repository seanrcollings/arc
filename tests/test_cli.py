"""Test the functionality of the CLI as a whole"""
from io import StringIO

from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest
from arc.errors import ScriptError


# pylint: disable=protected-access, missing-function-docstring
class TestCLI(BaseTest):
    def setUp(self):
        self.cli = self.create_cli()

    def test_register(self):
        assert "func1" in self.cli.scripts.keys()
        assert "func2" in self.cli.scripts.keys()

    def test_func1(self):
        self.cli("func1 x=2")
        self.cli.scripts["func1"].function.assert_called_with(x="2")

    def test_func2(self):
        self.cli("func2 x=4")
        self.cli.scripts["func2"].function.assert_called_with(x=4)

    def test_nonexistant_script(self):
        with self.assertRaises(ScriptError):
            self.cli("doesnotexist")

    def test_present_flags(self):
        self.cli.script(name="func3", options=[], flags=["--x"])(MagicMock())
        self.cli("func3 --x")
        self.cli.scripts["func3"].function.assert_called_with(x=True)

    def test_absent_flags(self):
        self.cli.script(name="func3", options=[], flags=["--x"])(MagicMock())
        self.cli("func3")
        self.cli.scripts["func3"].function.assert_called_with(x=False)

    def test_anon_script(self):
        self.cli.script(name="anon", options=["x"])(MagicMock())
        self.cli("x=2")
        self.cli.scripts["anon"].function.assert_called_with(x="2")
