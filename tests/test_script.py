"""Test the functionality of the Script class"""
from unittest.mock import MagicMock, create_autospec
from tests.base_test import BaseTest
from arc.script import Script
from arc.errors import ScriptError, ArcError
from arc.parser.data_types import FlagNode, OptionNode

# pylint: disable=protected-access, missing-function-docstring
class TestScript(BaseTest):
    def create_script(self, func, annotations, convert=True):
        func.__annotations__ = annotations
        func = create_autospec(func)
        return Script(name="test", function=func, convert=convert)

    def test_execution(self):
        script = self.create_script(
            lambda x, y, test: x, annotations={"y": int, "test": bool}
        )

        script(options=[OptionNode("x", "2"), OptionNode("y", "3")], flags=[])
        script.function.assert_called_with(x="2", y=3, test=False)

        script(
            options=[OptionNode("x", "2"), OptionNode("y", "3")],
            flags=[FlagNode("test")],
        )
        script.function.assert_called_with(x="2", y=3, test=True)

    def test_build_flags(self):
        script = self.create_script(lambda x, test: x, annotations={"test": bool})
        assert "test" in script.flags

    def test_nonexistant_options(self):
        script = self.create_script(
            lambda x, y, test: x, annotations={"y": int, "test": bool}
        )

        with self.assertRaises(ScriptError):
            script(options=[OptionNode("p", "2")], flags=[])

    def test_nonexistant_flag(self):
        script = self.create_script(lambda test: x, annotations={"test": bool})
        with self.assertRaises(ScriptError):
            script(options=[], flags=[FlagNode("none")])
