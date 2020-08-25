import importlib
from tests.base_test import BaseTest
from arc.errors import ArcError
from arc import Config
from arc.converter import BaseConverter
from arc.converter import input as inp


class TestConverter(BaseConverter):
    convert_to = "test"

    def convert(self, value):
        return int(value)


class TestInputConverters(BaseTest):
    def test_all(self):
        importlib.reload(inp)
        for name, converter in Config.converters.items():
            self.assertTrue(hasattr(inp, f"input_to_{name}"))

    def test_custom(self):
        Config.converters["test"] = TestConverter
        importlib.reload(inp)
        self.assertTrue(hasattr(inp, "input_to_test"))
