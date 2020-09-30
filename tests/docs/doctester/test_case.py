import unittest
import subprocess
from .main import get_executables


class TestDocs(unittest.TestCase):
    docs_dir = "../docs"

    def test_docs(self):
        executables = get_executables(self.docs_dir)
        for exe in executables:
            with self.subTest(exe.origin):
                try:
                    output, expected = exe.execute()
                    self.assertEqual(output, expected)
                except subprocess.CalledProcessError as e:
                    raise Exception(e.stderr.decode("utf-8")) from e
