from tests.script.base_script_test import BaseScriptTest
from arc.parser.data_types import ScriptNode, FlagNode, ArgNode, OptionNode
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
            self.create_script_node(
                options=[OptionNode("x", "2"), OptionNode("y", "3")],
            )
        )
        self.script1.function.assert_called_with(x="2", y=3, test=False)

        self.script1(
            self.create_script_node(
                options=[OptionNode("x", "2"), OptionNode("y", "3")],
                flags=[FlagNode("test")],
            )
        )
        self.script1.function.assert_called_with(x="2", y=3, test=True)

        self.script2(
            self.create_script_node(
                options=[
                    OptionNode("a", "test"),
                    OptionNode("b", "2"),
                    OptionNode("c", "2.5"),
                    OptionNode("d", "test"),
                    OptionNode("e", "1,2,3,4"),
                ],
                flags=[FlagNode("f")],
            )
        )
        self.script2.function.assert_called_with(
            a="test", b=2, c=2.5, d=b"test", e=["1", "2", "3", "4"], f=True
        )

    def test_build_args(self):

        with self.assertRaises(ScriptError):
            script = self.create_script(lambda *args: args)

        script = self.create_script(lambda **kwargs: kwargs)
        self.assertTrue(script.pass_kwargs)

    def test_validate_input(self):
        with self.assertRaises(ScriptError):
            self.script1(self.create_script_node(args=[ArgNode("test")]))
        self.assertEqual(len(self.script1.validation_errors), 1)

    def test_kwargs(self):
        script = self.create_script(lambda **kwargs: kwargs)

        script(self.create_script_node())
        script.function.assert_called_with()

        script(
            self.create_script_node(
                options=[OptionNode("test1", "2"), OptionNode("test2", "4")]
            )
        )
        script.function.assert_called_with(test1="2", test2="4")

        script = self.create_script(lambda a, **kwargs: kwargs, annotations={"a": int})
        script(
            self.create_script_node(
                options=[
                    OptionNode("test1", "2"),
                    OptionNode("test2", "4"),
                    OptionNode("a", "2"),
                ]
            )
        )
        script.function.assert_called_with(a=2, test1="2", test2="4")
