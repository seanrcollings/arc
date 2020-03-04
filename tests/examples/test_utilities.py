from io import StringIO
from unittest.mock import patch
from tests.base_test import BaseTest
from examples.utilities import cli, converse


class TestUtilities(BaseTest):
    def test_installed(self):
        assert cli.utilities[converse.name] is converse

    @patch('sys.stdout', new_callable=StringIO)
    def test_execute(self, mock_out):
        with patch("sys.argv", new=["dir", "converse:greet", "name=Sean"]):
            cli()
        assert "Howdy, Sean!" in mock_out.getvalue().strip()
