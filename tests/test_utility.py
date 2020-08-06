from unittest.mock import MagicMock
from io import StringIO
from tests.base_test import BaseTest
from arc import Utility
from arc.errors import ScriptError


# pylint: disable=protected-access, missing-function-docstring
class TestUtility(BaseTest):
    def setUp(self):
        self.util = self.create_util()
        self.cli = self.create_cli()
        self.cli.install_utilities(self.util)

    def test_register(self):
        assert self.util.name in self.cli.utilities.keys()

    def test_func1(self):
        self.cli("util:func1 x=2")
        self.cli.utilities["util"].scripts["func1"].function.assert_called_with(x="2")

    def test_func2(self):
        self.cli("util:func2 x=4")
        self.cli.utilities["util"].scripts["func2"].function.assert_called_with(x=4)

    def test_nonexistant_script(self):
        with self.assertRaises(ScriptError):
            self.cli("util:doesnotexist")

    def test_present_flags(self):
        self.util.script(name="func3", options=[], flags=["--x"])(MagicMock())
        self.cli("util:func3 --x")
        self.cli.utilities["util"].scripts["func3"].function.assert_called_with(x=True)

    def test_absent_flags(self):
        self.util.script(name="func3", options=[], flags=["--x"])(MagicMock())
        self.cli("util:func3")
        self.cli.utilities["util"].scripts["func3"].function.assert_called_with(x=False)

    def test_anon_script(self):
        self.util.script(name="anon", options=["x"])(MagicMock())
        self.cli("util: x=2")
        self.cli.utilities["util"].scripts["anon"].function.assert_called_with(x="2")
