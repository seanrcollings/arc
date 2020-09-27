import subprocess
from tests.base_test import BaseTest
from .doctester import test_docs_dir


class TestDocs(BaseTest):
    def test_docs(self):
        test_docs_dir("../docs")
