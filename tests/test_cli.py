"""Test the functionality of the CLI as a whole"""
from unittest.mock import MagicMock
from tests.base_test import BaseTest
from arc.errors import ScriptError
from arc import Utility


# pylint: disable=protected-access, missing-function-docstring
class TestCLI(BaseTest):
    def setUp(self):
        self.cli = self.create_cli()

    def test_register_utilities(self):
        util1 = Utility("util1")
        util2 = Utility("util2")
        self.cli.install_utilities(util1, util2)
        self.assertIn(util1, self.cli.utilities.values())
        self.assertIn(util2, self.cli.utilities.values())
