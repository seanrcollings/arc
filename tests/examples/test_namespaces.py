from io import StringIO
from unittest.mock import patch
from unittest import TestCase
from examples.namespaces import cli, converse


class TestNamespace(TestCase):
    def test_installed(self):
        assert cli.subcommands[converse.name] is converse

    @patch("sys.stdout", new_callable=StringIO)
    def test_execute(self, mock_out):
        cli("converse:greet name=Sean")
        self.assertIn("Howdy, Sean!", mock_out.getvalue().strip())
