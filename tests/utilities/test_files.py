import os
from io import StringIO
from unittest.mock import patch
from unittest import TestCase
from arc.utilities.files import files
from arc import run


class TestFiles(TestCase):
    def setUp(self):
        file = open("test.txt", "w+")
        file.write("test")
        file.close()

    def tearDown(self):
        os.remove("test.txt")

    def test_create(self):
        run(files, "create filename=create.txt")
        assert os.path.isfile("create.txt")
        os.remove("create.txt")

    @patch("sys.stdout", new_callable=StringIO)
    def test_read(self, mock_out):
        run(files, "read filename=test.txt")
        assert mock_out.getvalue().strip() == "test"

    def test_write(self):
        run(files, "append filename=test.txt write=test2")
        file = open("test.txt")
        assert file.read() == "testtest2"
        file.close()

    def test_delete(self):
        open("delete.txt", "w+").close()
        run(files, "delete filename=delete.txt")
        assert not os.path.isfile("delete.txt")
