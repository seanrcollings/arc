from io import StringIO
from unittest.mock import patch
from tests import BaseTest
from arc.utilities.debug import debug


class TestDebug(BaseTest):
    '''For now, just test if these execute at all, not what they return'''
    def setUp(self):
        self.cli = self.create_cli(utilities=[debug])

    def test_installed(self):
        assert debug is self.cli.utilities[debug.name]

    @patch("sys.stdout", new_callable=StringIO)
    def test_config(self, mock_out):
        with patch("sys.argv", new=["dir", "debug:config"]):
            self.cli()

    @patch("sys.stdout", new_callable=StringIO)
    def test_converters(self, mock_out):
        with patch("sys.argv", new=["dir", "debug:converters"]):
            self.cli()

    @patch("sys.stdout", new_callable=StringIO)
    def test_arcfile(self, mock_out):
        with patch("sys.argv", new=["dir", "debug:arcfile"]):
            self.cli()
