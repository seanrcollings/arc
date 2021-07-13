from io import StringIO
from unittest.mock import patch
from unittest import TestCase
from arc.builtin.debug import debug
from arc import CLI


class TestDebug(TestCase):
    """For now, just test if these execute at all, not what they return"""

    def setUp(self):
        self.cli = CLI()
        self.cli.install_command(debug)

    def test_installed(self):
        assert debug is self.cli.subcommands[debug.name]

    @patch("sys.stdout", new_callable=StringIO)
    def test_config(self, _):
        self.cli("debug:config")

    @patch("sys.stdout", new_callable=StringIO)
    def test_converters(self, _):
        self.cli("debug:converters")

    @patch("sys.stdout", new_callable=StringIO)
    def test_arcfile(self, _):
        self.cli("debug:arcfile")
