from tests.script.base_script_test import BaseScriptTest
from arc.parser.data_types import ArgNode, KEY_ARGUMENT, POS_ARGUMENT
from arc.script.keyword_script import KeywordScript
from arc.errors import ScriptError


class TestKeywordScript(BaseScriptTest):
    script_class = KeywordScript

    def __init__(self, *args, **kwargs):
        self.script1 = self.create_script(
            lambda x, y, test: x, annotations={"y": int, "test": bool}
        )
        self.script2 = self.create_script(
            lambda a, b, c, d, e, f: a,
            annotations={"b": int, "c": float, "d": bytes, "e": list, "f": bool},
        )

        super().__init__(*args, **kwargs)

    def test_execute(self):
        self.script1(
            self.command_node(
                args=[ArgNode("x", "2", KEY_ARGUMENT), ArgNode("y", "3", KEY_ARGUMENT)],
            )
        )
        self.script1.function.assert_called_with(x="2", y=3, test=False)

        self.script1(
            self.command_node(
                args=[
                    ArgNode("x", "2", KEY_ARGUMENT),
                    ArgNode("y", "3", KEY_ARGUMENT),
                    ArgNode("test", "true", KEY_ARGUMENT),
                ],
            )
        )
        self.script1.function.assert_called_with(x="2", y=3, test=True)

        self.script2(
            self.command_node(
                args=[
                    ArgNode("a", "test", KEY_ARGUMENT),
                    ArgNode("b", "2", KEY_ARGUMENT),
                    ArgNode("c", "2.5", KEY_ARGUMENT),
                    ArgNode("d", "test", KEY_ARGUMENT),
                    ArgNode("e", "1,2,3,4", KEY_ARGUMENT),
                    ArgNode("f", "true", KEY_ARGUMENT),
                ]
            )
        )
        self.script2.function.assert_called_with(
            a="test", b=2, c=2.5, d=b"test", e=["1", "2", "3", "4"], f=True
        )

    def test_build_args(self):
        with self.assertRaises(ScriptError):
            script = self.create_script(lambda *args: args)

        script = self.create_script(lambda **kwargs: kwargs)
        self.assertTrue(script._KeywordScript__pass_kwargs)

    def test_validate_input(self):
        with self.assertRaises(ScriptError):
            self.script1(self.command_node(args=[ArgNode("", "test", POS_ARGUMENT)]))
        self.assertEqual(len(self.script1.validation_errors), 1)

    def test_kwargs(self):
        script = self.create_script(lambda **kwargs: kwargs)

        script(self.command_node())
        script.function.assert_called_with()

        script(
            self.command_node(
                args=[
                    ArgNode("test1", "2", KEY_ARGUMENT),
                    ArgNode("test2", "4", KEY_ARGUMENT),
                ]
            )
        )
        script.function.assert_called_with(test1="2", test2="4")

        script = self.create_script(lambda a, **kwargs: kwargs, annotations={"a": int})
        script(
            self.command_node(
                args=[
                    ArgNode("test1", "2", KEY_ARGUMENT),
                    ArgNode("test2", "4", KEY_ARGUMENT),
                    ArgNode("a", "2", KEY_ARGUMENT),
                ]
            )
        )
        script.function.assert_called_with(a=2, test1="2", test2="4")

    def test_meta(self):
        script = self.create_script(
            lambda a, meta: meta, annotations={"a": int}, meta={"val": 2}
        )
        script(self.command_node(args=[ArgNode("a", "2", KEY_ARGUMENT)]))
        script.function.assert_called_with(a=2, meta={"val": 2})
