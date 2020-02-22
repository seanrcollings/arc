from tests.base_test import BaseTest
from unittest.mock import patch, MagicMock


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
