import os
from io import StringIO
from unittest.mock import patch
from tests.base_test import BaseTest
from arc.utilities.files import files


class TestFiles(BaseTest):
    def setUp(self):
        self.cli = self.create_cli(utilities=[files])
        file = open("test.txt", "w+")
        file.write("test")
        file.close()

    def tearDown(self):
        os.remove("test.txt")

    def test_create(self):
        with patch("sys.argv", new=["dir", "files:create", "filename=create.txt"]):
            self.cli()
        assert os.path.isfile("create.txt")
        os.remove("create.txt")

    @patch("sys.stdout", new_callable=StringIO)
    def test_read(self, mock_out):
        self.cli("files:read filename=test.txt")
        assert mock_out.getvalue().strip() == "test"

    def test_write(self):
        with patch(
            "sys.argv", new=["dir", "files:append", "filename=test.txt", "write=test2"]
        ):
            self.cli()
        file = open("test.txt")
        assert file.read() == "testtest2"
        file.close()

    def test_delete(self):
        open("delete.txt", "w+").close()
        with patch("sys.argv", new=["dir", "files:delete", "filename=delete.txt"]):
            self.cli()
        assert not os.path.isfile("delete.txt")
