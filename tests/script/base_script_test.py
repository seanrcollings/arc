from unittest.mock import create_autospec
from typing import Type
from tests.base_test import BaseTest

from arc.script.script import Script
from arc.errors import ScriptError
from arc.parser.data_types import ArgNode, FLAG, POS_ARGUMENT, KEY_ARGUMENT, CommandNode


class BaseScriptTest(BaseTest):
    script_class: Type[Script]

    def create_script(self, func, annotations={}, *args, **kwargs):
        if len(func.__annotations__) == 0:
            func.__annotations__ = annotations
        func = create_autospec(func)
        return self.script_class(name="test", function=func, *args, **kwargs)  # type: ignore

    def command_node(self, name="test", args=[]):
        return CommandNode(name, args)

    def test_nonexistant_args(self):
        script = self.create_script(
            lambda x, y, test: x, annotations={"y": int, "test": bool}
        )

        with self.assertRaises(ScriptError):
            script(self.command_node(args=[ArgNode("p", "2", KEY_ARGUMENT)]))

    def test_nonexistant_flag(self):
        script = self.create_script(lambda test: test, annotations={"test": bool})
        with self.assertRaises(ScriptError):
            script(self.command_node(args=[ArgNode("none", "true", KEY_ARGUMENT)]))
