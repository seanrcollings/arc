from io import StringIO
from unittest.mock import patch

from tests import BaseTest
from examples.basic_example import cli


class TestBaseExample(BaseTest):
    @patch('sys.stdout', new_callable=StringIO)
    def test_example_(self, mock_out):
        with patch("sys.argv", new=["dir", "greet", "name=Sean"]):
            cli()
        assert mock_out.getvalue().strip() == "Hello, Sean!"
