from io import StringIO
from unittest.mock import patch
from tests.base_test import BaseTest
from arc import CLI


#pylint: disable=protected-access, missing-function-docstring
class TestCLI(BaseTest):
    def test_creation(self):
        cli = CLI()
        assert isinstance(cli, CLI)

    def test_register(self):
        cli = self.create_cli()
        assert "func1" in cli.scripts.keys()
        assert "func2" in cli.scripts.keys()

    @patch('sys.stdout', new_callable=StringIO)
    def test_func1(self, mock_out):
        cli = self.create_cli()
        with patch('sys.argv', new=["dir", 'func1', "x=2"]):
            cli()
        assert mock_out.getvalue().strip("\n") == "2"

    @patch('sys.stdout', new_callable=StringIO)
    def test_func2(self, mock_out):
        cli = self.create_cli()
        with patch('sys.argv', new=["dir", 'func2', "x=2"]):
            cli()
        assert mock_out.getvalue().strip("\n") == "4"

    @patch('sys.stdout', new_callable=StringIO)
    def test_nonexistant_script(self, mock_out):
        cli = self.create_cli()
        with patch('sys.argv', new=["dir", 'doesnotexist']):
            cli()
        assert mock_out.getvalue().strip("\n") == "That command does not exist"