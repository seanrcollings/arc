from io import StringIO
from unittest.mock import patch

from tests.base_test import BaseTest
from examples.basic_example import cli


class TestBaseExample(BaseTest):
    @patch("sys.stdout", new_callable=StringIO)
    def test_example_(self, mock_out):
        cli("greet name=Sean")
        self.assertEqual(mock_out.getvalue().strip(), "Hello, Sean!")
