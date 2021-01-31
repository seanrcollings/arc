from tests.script.base_script_test import BaseScriptTest

from arc.errors import ScriptError
from arc.script.positional_script import PositionalScript
from arc.parser.data_types import ArgNode, POS_ARGUMENT


class TestPositionalScript(BaseScriptTest):
    script_class = PositionalScript

    def test_args(self):
        script = self.create_script(lambda *args: args)
        script(self.command_node())
        script.function.assert_called_with()

        script(
            self.command_node(
                args=[
                    ArgNode("", "test1", POS_ARGUMENT),
                    ArgNode("", "test2", POS_ARGUMENT),
                ]
            )
        )
        script.function.assert_called_with("test1", "test2")

    def test_build_args(self):
        with self.assertRaises(ScriptError):
            script = self.create_script(lambda **kwargs: kwargs)

        script = self.create_script(lambda *args: args)
        self.assertTrue(script._PositionalScript__pass_args)

    def test_meta(self):
        script = self.create_script(
            lambda a, meta: meta, annotations={"a": int}, meta={"val": 2}
        )
        script(self.command_node(args=[ArgNode("", "2", POS_ARGUMENT)]))
        script.function.assert_called_with(a=2, meta={"val": 2})
