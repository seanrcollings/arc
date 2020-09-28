import subprocess
from tests.base_test import BaseTest
from .doctester import test_docs_dir


class DocError(Exception):
    pass


class TestDocs(BaseTest):
    def test_docs(self):
        try:
            test_docs_dir("../docs")
        except subprocess.CalledProcessError as e:
            raise DocError(e.stderr.decode("utf-8"))
