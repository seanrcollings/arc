from unittest.mock import patch
from io import StringIO, TextIOWrapper
from tests.base_test import BaseTest
from arc import Utility


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
    def test_context_manager(self, mock_out):
        cli = self.create_cli()
        util = self.create_util(context_manager=StringIO("context"))
        util._install_script(lambda files: print(files.getvalue()), "files",
                             None, True)
        cli.install_utilities(util)
        with patch('sys.argv', new=["dir", 'util:files']):
            cli()
        assert mock_out.getvalue().strip("\n") == "context"