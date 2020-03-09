'''Test the functionality of the CLI as a whole'''
from io import StringIO
from unittest.mock import patch
from tests.base_test import BaseTest
from arc import CLI
import sys


#pylint: disable=protected-access, missing-function-docstring
class TestCLI(BaseTest):
    def setUp(self):
        self.cli = self.create_cli()

    def test_register(self):
        assert "func1" in self.cli.scripts.keys()
        assert "func2" in self.cli.scripts.keys()

    @patch('sys.stdout', new_callable=StringIO)
    def test_func1(self, mock_out):
        with patch('sys.argv', new=["dir", 'func1', "x=2"]):
            self.cli()
        assert mock_out.getvalue().strip("\n") == "2"

    @patch('sys.stdout', new_callable=StringIO)
    def test_func2(self, mock_out):
        with patch('sys.argv', new=["dir", 'func2', "x=2"]):
            self.cli()
        assert mock_out.getvalue().strip("\n") == "4"

    @patch('sys.stdout', new_callable=StringIO)
    def test_nonexistant_script(self, mock_out):
        with patch('sys.argv', new=["dir", 'doesnotexist']):
            self.cli()
        assert mock_out.getvalue().strip("\n") == "That command does not exist"

    @patch('sys.stdout', new_callable=StringIO)
    def test_flags(self, mock_out):
        self.cli._install_script(name="func3",
                                 function=lambda x: print(x),
                                 options=[],
                                 flags=["--x"])

        with patch('sys.argv', new=["dir", 'func3', "--x"]):
            self.cli()
        assert mock_out.getvalue().strip("\n") == "True"

        mock_out.truncate(0)
        mock_out.seek(0)

        with patch('sys.argv', new=["dir", 'func3']):
            self.cli()
        assert mock_out.getvalue().strip("\n") == "False"

    @patch('sys.stdout', new_callable=StringIO)
    def test_pass_args(self, mock_out):
        self.cli._install_script(name="args",
                                 function=lambda *x, flag: print(*x),
                                 flags=["--flag"],
                                 pass_args=True)
        with patch('sys.argv', new=["dir", 'args', "test=4", "test2",
                                    "test3"]):
            self.cli()
        assert mock_out.getvalue().strip("\n") == "test=4 test2 test3"

    @patch('sys.stdout', new_callable=StringIO)
    def test_pass_kwargs(self, mock_out):
        self.cli._install_script(name="kwargs",
                                 function=lambda x, y, flag: print(x, y),
                                 flags=["--flag"],
                                 pass_kwargs=True)
        with patch('sys.argv', new=["dir", 'kwargs', "x=4", "y=4"]):
            self.cli()
        assert mock_out.getvalue().strip("\n") == "4 4"
