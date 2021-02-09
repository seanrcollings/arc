from io import StringIO
from unittest.mock import patch

from unittest import TestCase
from examples.basic_example import cli


class TestBaseExample(TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_example_(self, mock_out):
        cli("greet name=Sean")
        self.assertEqual(mock_out.getvalue().strip(), "Hello, Sean!")
