""" Testing main module
to run, use
    python3 -m tests [TEST NAME]
    if no test name is provided, it will run the entire test suite
"""
import unittest
import os

# Set the CWD so the correct .arc file gets loaded
dirname, filename = os.path.split(os.path.abspath(__file__))
os.chdir(dirname)

# Tests
# pylint: disable=unused-import, wrong-import-position, unused-wildcard-import, wildcard-import
from tests.test_cli import *
from tests.test_group import *
from tests.command import *
from tests.converter import *
from tests.autocomplete import *
from tests.examples import *
from tests.utilities import *
from tests.parser import *
from tests.test_context import *

# from tests.docs import *

if __name__ == "__main__":
    unittest.main()
