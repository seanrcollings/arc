import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest
from arc.utilities import https


class TestHTTPS(BaseTest):
    def setUp(self):
        self.cli = self.create_cli(utilities=[https])

    @patch('http.client.HTTPResponse.read', new_callable=MagicMock)
    @patch("sys.stdout", new_callable=StringIO)
    def test_get(self, mock_out, mock_connection):
        mock_connection.return_value = "test"
        with patch("sys.argv",
                   new=[
                       "dir", "https:get", "url=www.example.com",
                       "endpoint=/test"
                   ]):
            self.cli()
        assert mock_out.getvalue().strip() == "test"
