from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest
from arc.errors import ArcError


# pylint: disable=protected-access, missing-function-docstring
class TestConverters(BaseTest):
    def test_string(self):
        cli = self.create_cli()
        func = MagicMock()
        cli.script(name="string", options=["name"])(function=func)
        with patch("sys.argv", new=["dir", "string", "name=Sean"]):
            cli()
        func.assert_called_with(name="Sean")

    def test_int(self):
        cli = self.create_cli()
        func = MagicMock()
        cli.script(name="int", options=["<int:number>"])(function=func)
        with patch("sys.argv", new=["dir", "int", "number=5"]):
            cli()
        func.assert_called_with(number=5)

    def test_float(self):
        cli = self.create_cli()
        func = MagicMock()
        cli.script(name="float", options=["<float:number>"])(function=func)
        with patch("sys.argv", new=["dir", "float", "number=4.5"]):
            cli()
        func.assert_called_with(number=4.5)

    def test_byte(self):
        cli = self.create_cli()
        func = MagicMock()
        cli.script(name="byte", options=["<byte:string>"])(function=func)
        with patch("sys.argv", new=["dir", "byte", "string=hello"]):
            cli()
        func.assert_called_with(string=b"hello")

    def test_bool(self):
        cli = self.create_cli()
        func = MagicMock()
        cli.script(name="bool", options=["<bool:test>"])(function=func)
        with patch("sys.argv", new=["dir", "bool", "test='anything'"]):
            cli()
        func.assert_called_with(test=True)

    def test_intbool(self):
        cli = self.create_cli()
        func = MagicMock()
        cli.script(name="ibool", options=["<ibool:test>"])(function=func)
        with patch("sys.argv", new=["dir", "ibool", "test=0"]):
            cli()
        func.assert_called_with(test=False)
        with patch("sys.argv", new=["dir", "ibool", "test=2"]):
            cli()
        func.assert_called_with(test=True)

    def test_strbool(self):
        cli = self.create_cli()
        func = MagicMock()
        cli.script(name="sbool", options=["<sbool:test>"])(function=func)
        with patch("sys.argv", new=["dir", "sbool", "test=False"]):
            cli()
        func.assert_called_with(test=False)
        with patch("sys.argv", new=["dir", "sbool", "test=True"]):
            cli()
        func.assert_called_with(test=True)

    def test_list(self):
        cli = self.create_cli()
        func = MagicMock()
        cli.script(name="list", options=["<list:test>"])(function=func)
        with patch("sys.argv", new=["dir", "list", "test=1,2,3,4"]):
            cli()
        func.assert_called_with(test=["1", "2", "3", "4"])
        # with patch("sys.argv", new=["dir", "list", "test=2"]):
        #     cli()
        # func.assert_called_with(test=["2"])

    # def test_invalid_converters(self):
    #     cli = self.create_cli()
    #     func = MagicMock()
    #     with self.assertRaises(ArcError):
    #         cli.script(name="string",
    #                    options=["<str:name><int:name>"])(function=func)
    #     with self.assertRaises(ArcError):
    #         cli.script(name="string", options=["<str::name>"])(function=func)
