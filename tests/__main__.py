'''
Testing main module
to run, use
    python3 -m tests [TEST NAME]
    if no test name is provided, it will run the entire test suite
'''
import sys
import unittest
# Tests
# pylint: disable=unused-import
from tests.test_cli import TestCLI
from tests.test_utility import TestUtility
from tests.test_converters import TestConverters

if __name__ == "__main__":
    unittest.main()
