import importlib
from unittest import TestCase
from arc import arc_config
from arc.convert import BaseConverter
from arc.convert import input as inp


class MockConverter(BaseConverter):
    convert_to = "test"

    def convert(self, value):
        return int(value)


class TestInputConverters(TestCase):
    def test_all(self):
        importlib.reload(inp)
        for name in arc_config.converters:
            self.assertTrue(hasattr(inp, f"input_to_{name}"))

    def test_custom(self):
        arc_config.converters["test"] = MockConverter
        importlib.reload(inp)
        self.assertTrue(hasattr(inp, "input_to_test"))
