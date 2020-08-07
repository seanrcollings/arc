"""Test the functionality of the Script class"""
from unittest.mock import MagicMock
from tests.base_test import BaseTest
from arc.script import Script
from arc.errors import ScriptError, ArcError
from arc.parser.data_types import FlagNode, OptionNode

# pylint: disable=protected-access, missing-function-docstring
class TestScript(BaseTest):
    def create_script(self, options=None, flags=None, convert=True):
        func = MagicMock()
        return Script(
            name="test", function=func, options=options, flags=flags, convert=convert
        )

    def test_execution(self):
        script = self.create_script(options=["x", "<int:y>"], flags=["--test"])

        script(options=[OptionNode("x", "2"), OptionNode("y", "3")], flags=[])
        script.function.assert_called_with(x="2", y=3, test=False)

        script(
            options=[OptionNode("x", "2"), OptionNode("y", "3")],
            flags=[FlagNode("test")],
        )
        script.function.assert_called_with(x="2", y=3, test=True)

    def test_build_flags(self):
        script = self.create_script(options=["x", "<int:y>"], flags=["--test"])
        assert "test" in script.flags

        with self.assertRaises(ArcError):
            script = self.create_script(options=["x", "<int:y>"], flags=["++test"])

    def test_nonexistant_options(self):
        script = self.create_script(options=["x", "<int:y>"], flags=["--test"])
        with self.assertRaises(ScriptError):
            script(options=[OptionNode("p", "2")], flags=[])

    def test_nonexistant_flag(self):
        script = self.create_script(options=[], flags=["--test"])
        with self.assertRaises(ScriptError):
            script(options=[], flags=[FlagNode("none")])
