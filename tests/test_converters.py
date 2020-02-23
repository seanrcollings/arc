from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest
from arc.errors import *


#pylint: disable=protected-access, missing-function-docstring
class TestConverters(BaseTest):
    def test_string(self):
        cli = self.create_cli()
        func = MagicMock()
        cli._install_script(function=func,
                            name="string",
                            options=["name"],
                            named_arguements=True)
        with patch('sys.argv', new=["dir", 'string', "name=Sean"]):
            cli()
        func.assert_called_with(name="Sean")

    def test_int(self):
        cli = self.create_cli()
        func = MagicMock()
        cli._install_script(function=func,
                            name="int",
                            options=["<int:number>"],
                            named_arguements=True)
        with patch('sys.argv', new=["dir", 'int', "number=5"]):
            cli()
        func.assert_called_with(number=5)

    def test_float(self):
        cli = self.create_cli()
        func = MagicMock()
        cli._install_script(function=func,
                            name="float",
                            options=["<float:number>"],
                            named_arguements=True)
        with patch('sys.argv', new=["dir", 'float', "number=4.5"]):
            cli()
        func.assert_called_with(number=4.5)

    def test_byte(self):
        cli = self.create_cli()
        func = MagicMock()
        cli._install_script(function=func,
                            name="byte",
                            options=["<byte:string>"],
                            named_arguements=True)
        with patch('sys.argv', new=["dir", 'byte', "string=hello"]):
            cli()
        func.assert_called_with(string=b'hello')

    def test_bool(self):
        cli = self.create_cli()
        func = MagicMock()
        cli._install_script(function=func,
                            name="bool",
                            options=["<bool:test>"],
                            named_arguements=True)
        with patch('sys.argv', new=["dir", 'bool', "test=''"]):
            cli()
        func.assert_called_with(test=True)
        with patch('sys.argv', new=["dir", 'bool', "test='anything'"]):
            cli()
        func.assert_called_with(test=True)

    def test_intbool(self):
        cli = self.create_cli()
        func = MagicMock()
        cli._install_script(function=func,
                            name="ibool",
                            options=["<ibool:test>"],
                            named_arguements=True)
        with patch('sys.argv', new=["dir", 'ibool', "test=0"]):
            cli()
        func.assert_called_with(test=False)
        with patch('sys.argv', new=["dir", 'ibool', "test=2"]):
            cli()
        func.assert_called_with(test=True)

    def test_strbool(self):
        cli = self.create_cli()
        func = MagicMock()
        cli._install_script(function=func,
                            name="sbool",
                            options=["<sbool:test>"],
                            named_arguements=True)
        with patch('sys.argv', new=["dir", 'sbool', "test=False"]):
            cli()
        func.assert_called_with(test=False)
        with patch('sys.argv', new=["dir", 'sbool', "test=True"]):
            cli()
        func.assert_called_with(test=True)

    def test_list(self):
        cli = self.create_cli()
        func = MagicMock()
        cli._install_script(function=func,
                            name="list",
                            options=["<list:test>"],
                            named_arguements=True)
        with patch('sys.argv', new=["dir", 'list', "test=1,2,3,4"]):
            cli()
        func.assert_called_with(test=['1', '2', '3', '4'])
        with patch('sys.argv', new=["dir", 'list', "test=2"]):
            cli()
        func.assert_called_with(test=['2'])

    def test_invalid_converters(self):
        cli = self.create_cli()
        func = MagicMock()
        with self.assertRaises(ArcError):
            cli._install_script(function=func,
                                name="string",
                                options=["<str:name><int:name>"],
                                named_arguements=True)
        with self.assertRaises(ArcError):
            cli._install_script(function=func,
                                name="string",
                                options=["<str::name>"],
                                named_arguements=True)
