import importlib
from unittest import TestCase
from arc import config
from arc.convert import BaseConverter
from arc.convert import input as inp


class TestConverter(BaseConverter):
    convert_to = "test"

    def convert(self, value):
        return int(value)


class TestInputConverters(TestCase):
    def test_all(self):
        importlib.reload(inp)
        for name, converter in config.converters.items():
            self.assertTrue(hasattr(inp, f"input_to_{name}"))

    def test_custom(self):
        config.converters["test"] = TestConverter
        importlib.reload(inp)
        self.assertTrue(hasattr(inp, "input_to_test"))
