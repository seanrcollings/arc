from tests.script.base_script_test import BaseScriptTest
from arc.script.legacy_script import LegacyScript
from arc.errors import ScriptError
from arc.parser.data_types import FlagNode, OptionNode, ArgNode
from arc.convert.converters import *
from arc import config


class TestLegacyScript(BaseScriptTest):
    script_class = LegacyScript

    def test_execution(self):
        script = self.create_script(
            lambda x, y, test: x, annotations={"y": int, "test": bool}
        )

        script(
            self.create_script_node(
                options=[OptionNode("x", "2"), OptionNode("y", "3")],
            )
        )
        script.function.assert_called_with(x="2", y=3, test=False)

        script(
            self.create_script_node(
                options=[OptionNode("x", "2"), OptionNode("y", "3")],
                flags=[FlagNode("test")],
            )
        )
        script.function.assert_called_with(x="2", y=3, test=True)

        script = self.create_script(
            lambda a, b, c, d, e, f: a,
            annotations={"b": int, "c": float, "d": bytes, "e": list, "f": bool},
        )
        script(
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
        script.function.assert_called_with(
            a="test", b=2, c=2.5, d=b"test", e=["1", "2", "3", "4"], f=True
        )

    def test_build_script(self):
        script = self.create_script(
            lambda a, b, c, d, e: a,
            annotations={"b": int, "c": float, "d": bytes, "e": list},
        )

        with self.assertRaises(AttributeError):
            config.get_converter(script.options["a"].get_converter_name())

        self.assertIs(
            config.get_converter(script.options["b"].get_converter_name()), IntConverter
        )
        self.assertIs(
            config.get_converter(script.options["c"].get_converter_name()),
            FloatConverter,
        )
        self.assertIs(
            config.get_converter(script.options["d"].get_converter_name()),
            BytesConverter,
        )
        self.assertIs(
            config.get_converter(script.options["e"].get_converter_name()),
            ListConverter,
        )

    def test_build_flags(self):
        script = self.create_script(lambda x, test: x, annotations={"test": bool})
        self.assertIn("test", script.flags)
        self.assertFalse(script.flags["test"].value)

        script = self.create_script(lambda x, test=True: x, annotations={"test": bool})
        self.assertTrue(script.flags["test"].value)

    def test_args(self):
        script = self.create_script(lambda *args: args)
        script(self.create_script_node())
        script.function.assert_called_with()

        script(self.create_script_node(args=[ArgNode("test1"), ArgNode("test2")]))
        script.function.assert_called_with("test1", "test2")

        with self.assertRaises(ScriptError):
            self.create_script(lambda x, *args: x)

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

    def test_meta(self):
        script = self.create_script(
            lambda a, meta: meta, annotations={"a": int}, meta={"val": 2}
        )
        script(self.create_script_node(options=[OptionNode("a", "2")]))
        script.function.assert_called_with(a=2, meta={"val": 2})
