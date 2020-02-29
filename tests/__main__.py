''' Testing main module
to run, use
    python3 -m tests [TEST NAME]
    if no test name is provided, it will run the entire test suite
'''
import unittest
import os

# Set the CWD so the correct .arc file gets loaded
dirname, filename = os.path.split(os.path.abspath(__file__))
os.chdir(dirname)

# Tests
# pylint: disable=unused-import
from tests.test_cli import TestCLI
from tests.test_utility import TestUtility
from tests.test_converters import TestConverters

if __name__ == "__main__":
    unittest.main()
