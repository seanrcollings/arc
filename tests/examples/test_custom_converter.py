from io import StringIO
from unittest.mock import patch
from unittest import TestCase
from examples.custom_converter import Circle, cli


class TestCustomConverter(TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_command(self, mock_out):
        circle = Circle(4)
        cli("circle --new-circle 4")
        assert mock_out.getvalue().strip() == str(circle)
