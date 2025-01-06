from typing import Annotated
import pytest
from unittest.mock import Mock

import arc
from arc.types.default import Default
import arc.typing as at
from arc.types.type_info import TypeInfo
from arc.types.type_arg import TypeArg
from arc.types.aliases import Alias


@pytest.fixture
def type_info():
    mock_annotation = Mock(spec=at.Annotation)
    mock_origin = Mock()
    mock_sub_types = (Mock(spec=TypeInfo),)
    mock_annotations = (Mock(spec=TypeArg),)
    mock_name = "TestType"

    return TypeInfo(
        original_type=mock_annotation,
        origin=mock_origin,
        sub_types=mock_sub_types,
        annotations=mock_annotations,
        name=mock_name,
    )


class TypeArgMock(TypeArg):
    __slots__ = ("mode",)

    def __init__(self, mode: str):
        self.mode = mode


class TypeArgDefaultMock(TypeArg):
    __slots__ = ("mode", "value")

    def __init__(self, mode: str = Default("r"), value: str = Default("w")):
        self.mode = mode
        self.value = value


class TestTypeArg:
    def test_type_arg(self, type_info):
        type_arg = TypeArgMock("r")
        type_info.annotations = (type_arg,)
        assert type_info.type_arg == type_arg

    def test_type_arg_multiple(self, type_info):
        mock_type_arg1 = TypeArgMock("r")
        mock_type_arg2 = TypeArgMock("w")
        type_info.annotations = (mock_type_arg1, mock_type_arg2)
        assert type_info.type_arg == mock_type_arg1 | mock_type_arg2
        assert type_info.type_arg.mode == "w"

    def test_type_arg_default(self, type_info):
        type_arg = TypeArgDefaultMock()
        type_info.annotations = (type_arg,)
        assert type_info.type_arg == type_arg
        assert type_info.type_arg.mode.value == "r"

    def test_type_arg_default_multiple(self, type_info):
        # TypeArgs are mered together with priority given to the rightmost value
        type_arg1 = TypeArgDefaultMock(mode="test", value="r")
        type_arg2 = TypeArgDefaultMock(mode="w")
        type_info.annotations = (type_arg1, type_arg2)
        assert type_info.type_arg == type_arg1 | type_arg2
        assert type_info.type_arg.mode == "w"
        assert type_info.type_arg.value == "r"

    def test_type_arg_none(self, type_info):
        type_info.annotations = ()
        assert type_info.type_arg is None


def test_middleware(type_info):
    mock_callable = Mock()
    type_info.annotations = (mock_callable,)
    assert type_info.middleware == [mock_callable]


def test_middleware_none(type_info):
    type_info.annotations = ()
    assert type_info.middleware == []


TestType = Annotated[str, arc.Option(name="test", short="t")]

NestedTestType = Annotated[TestType, arc.Option(name="nested", short="n")]


class TestParamInfo:
    def test_param_info(self, type_info):
        info = arc.Option(name="test")
        type_info.annotations = (info,)
        assert type_info.param_info == info

    def test_param_info_multiple(self, type_info):
        info1 = arc.Option(name="test1")
        info2 = arc.Option(name="test2")
        type_info.annotations = (info1, info2)
        assert type_info.param_info == info2

    def test_param_info_none(self, type_info):
        type_info.annotations = ()
        assert type_info.param_info is None

    def test_usage(self):

        @arc.command
        def command(type: TestType):
            return type

        # 0 is the --help flag
        param = list(command.param_def.all_params())[1]
        assert param.param_name == "test"
        assert param.short_name == "t"

        assert command("--test test") == "test"
        assert command("-t test") == "test"

    def test_nested_usage(self):
        @arc.command
        def command(nested: NestedTestType):
            return nested

        param = list(command.param_def.all_params())[1]
        assert param.param_name == "nested"
        assert param.short_name == "n"

        assert command("--nested test") == "test"
