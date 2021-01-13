from unittest.mock import create_autospec
from typing import Type
from tests.base_test import BaseTest

from arc.script.script import Script
from arc.errors import ScriptError
from arc.parser.data_types import ScriptNode, OptionNode, FlagNode


class BaseScriptTest(BaseTest):
    script_class: Type[Script]

    def create_script(self, func, annotations={}, *args, **kwargs):
        if len(func.__annotations__) == 0:
            func.__annotations__ = annotations
        func = create_autospec(func)
        return self.script_class(name="test", function=func, *args, **kwargs)  # type: ignore

    def create_script_node(self, name="test", options=[], flags=[], args=[]):
        return ScriptNode(name, options, flags, args)

    def test_nonexistant_options(self):
        script = self.create_script(
            lambda x, y, test: x, annotations={"y": int, "test": bool}
        )

        with self.assertRaises(ScriptError):
            script(self.create_script_node(options=[OptionNode("p", "2")]))

    def test_nonexistant_flag(self):
        script = self.create_script(lambda test: test, annotations={"test": bool})
        with self.assertRaises(ScriptError):
            script(self.create_script_node(flags=[FlagNode("none")]))
