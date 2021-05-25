from unittest import TestCase
from unittest.mock import patch
from io import StringIO

from arc import CLI


# from arc.autocomplete._autocomplete import AutoComplete


class TestAutoCompleteFish(TestCase):
    def setUp(self):
        self.cli = CLI("tool")
        self.cli.autocomplete()

        @self.cli.subcommand()
        def func1(x):
            ...

        @func1.subcommand()
        def subcommand():
            ...

        @self.cli.subcommand()
        def func2(x: int):
            ...

    @patch("sys.stdout", new_callable=StringIO)
    def test_command_completion(self, mock_out: StringIO):
        self.cli("_autocomplete:fish command_str='tool'")
        self.assertEqual(
            mock_out.getvalue().strip(), "--help\tFLAG\n--version\tFLAG\nfunc1\t\nfunc2"
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_subcommand_completion(self, mock_out: StringIO):
        self.cli("_autocomplete:fish command_str='tool func1:'")
        self.assertEqual(mock_out.getvalue().strip(), "x=\tstr\nfunc1:subcommand")

    @patch("sys.stdout", new_callable=StringIO)
    def test_options_completion(self, mock_out: StringIO):
        self.cli("_autocomplete:fish command_str='tool func1 '")
        self.assertEqual(mock_out.getvalue().strip(), "x=\tstr")
