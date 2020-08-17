"""Test the functionality of the Script class"""
from unittest.mock import create_autospec
from tests.base_test import BaseTest
from arc.script import Script
from arc.errors import ScriptError
from arc.parser.data_types import FlagNode, OptionNode
from arc.converter.converters import *

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

        script = self.create_script(
            lambda a, b, c, d, e, f: a,
            annotations={"b": int, "c": float, "d": bytes, "e": list, "f": bool},
        )
        script(
            options=[
                OptionNode("a", "test"),
                OptionNode("b", "2"),
                OptionNode("c", "2.5"),
                OptionNode("d", "test"),
                OptionNode("e", "1,2,3,4"),
            ],
            flags=[FlagNode("f")],
        )
        script.function.assert_called_with(
            a="test", b=2, c=2.5, d=b"test", e=["1", "2", "3", "4"], f=True
        )

    def test_build_script(self):
        script = self.create_script(
            lambda a, b, c, d, e: a,
            annotations={"b": int, "c": float, "d": bytes, "e": list},
        )
        self.assertIs(script.options["a"].converter, StringConverter)
        self.assertIs(script.options["b"].converter, IntConverter)
        self.assertIs(script.options["c"].converter, FloatConverter)
        self.assertIs(script.options["d"].converter, BytesConverter)
        self.assertIs(script.options["e"].converter, ListConverter)

    def test_build_flags(self):
        script = self.create_script(lambda x, test: x, annotations={"test": bool})
        self.assertIn("test", script.flags)
        self.assertFalse(script.flags["test"].value)

        script = self.create_script(lambda x, test=True: x, annotations={"test": bool})
        self.assertTrue(script.flags["test"].value)

    def test_nonexistant_options(self):
        script = self.create_script(
            lambda x, y, test: x, annotations={"y": int, "test": bool}
        )

        with self.assertRaises(ScriptError):
            script(options=[OptionNode("p", "2")], flags=[])

    def test_nonexistant_flag(self):
        script = self.create_script(lambda test: test, annotations={"test": bool})
        with self.assertRaises(ScriptError):
            script(options=[], flags=[FlagNode("none")])
