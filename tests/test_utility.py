from unittest.mock import patch
from io import StringIO
from tests.base_test import BaseTest
from arc import Utility


#pylint: disable=protected-access, missing-function-docstring
class TestUtility(BaseTest):
    def test_create(self):
        util = self.create_util()
        assert isinstance(util, Utility)

    def test_register(self):
        cli = self.create_cli()
        util = self.create_util()
        cli.install_utilities(util)
        assert util.name in cli.utilities.keys()

    @patch('sys.stdout', new_callable=StringIO)
    def test_func1(self, mock_out):
        cli = self.create_cli()
        util = self.create_util()
        cli.install_utilities(util)
        with patch('sys.argv', new=["dir", 'util:func1', "x=2"]):
            cli()
        assert mock_out.getvalue().strip("\n") == "2"

    @patch('sys.stdout', new_callable=StringIO)
    def test_func2(self, mock_out):
        cli = self.create_cli()
        util = self.create_util()
        cli.install_utilities(util)
        with patch('sys.argv', new=["dir", 'util:func2', "x=2"]):
            cli()
        assert mock_out.getvalue().strip("\n") == "4"

    @patch('sys.stdout', new_callable=StringIO)
    def test_nonexistant_script(self, mock_out):
        cli = self.create_cli()
        util = self.create_util()
        cli.install_utilities(util)
        with patch('sys.argv', new=["dir", 'util:doesnotexist']):
            cli()
        assert mock_out.getvalue().strip("\n") == "That command does not exist"

    @patch('sys.stdout', new_callable=StringIO)
    def test_flags(self, mock_out):
        util = self.create_util()
        cli = self.create_cli(utilities=[util])
        util.script(name="func3", options=[],
                    flags=["--x"])(function=lambda x: print(x))

        with patch('sys.argv', new=["dir", 'util:func3', "--x"]):
            cli()
        assert mock_out.getvalue().strip("\n") == "True"

        mock_out.truncate(0)
        mock_out.seek(0)

        with patch('sys.argv', new=["dir", 'util:func3']):
            cli()
        assert mock_out.getvalue().strip("\n") == "False"

    @patch('sys.stdout', new_callable=StringIO)
    def test_anon_script(self, mock_out):
        util = self.create_util()
        cli = self.create_cli(utilities=[util])
        util.script(name="anon", options=["x"])(lambda x: print(x))
        with patch("sys.argv", new=["dir", "util:", "x=2"]):
            cli()
        assert mock_out.getvalue().strip("\n") == "2"

    @patch('sys.stdout', new_callable=StringIO)
    def test_no_args_script(self, mock_out):
        util = self.create_util()
        cli = self.create_cli(utilities=[util])
        util.script(name="no_args")(lambda: print("no_args"))
        with patch("sys.argv", new=["dir", "util:"]):
            cli()
        assert mock_out.getvalue().strip("\n") == "no_args"