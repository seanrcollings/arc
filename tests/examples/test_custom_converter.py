from io import StringIO
from unittest.mock import patch
from tests.base_test import BaseTest
from examples.custom_converter import Config, CircleConverter, Circle, cli


class TestCustomConverter(BaseTest):
    def test_exists(self):
        assert Config.converters["circle"] is CircleConverter

    @patch('sys.stdout', new_callable=StringIO)
    def test_command(self, mock_out):
        circle = Circle(4)
        with patch("sys.argv", new=["dir", "circle", "new_circle=4"]):
            cli()
        assert mock_out.getvalue().strip() == str(circle)
