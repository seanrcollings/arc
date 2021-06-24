import importlib
from typing import _SpecialForm
from arc.convert import BaseConverter, register, input as inp, converter_mapping


class MockedType:
    ...


@register(MockedType)
class MockConverter(BaseConverter):
    def convert(self, value):
        return int(value)


def test_all():
    importlib.reload(inp)
    for kind in converter_mapping:
        if isinstance(kind, _SpecialForm):
            continue

        assert hasattr(inp, f"input_to_{kind.__name__}")


def test_custom():
    importlib.reload(inp)
    assert hasattr(inp, "input_to_MockedType")
