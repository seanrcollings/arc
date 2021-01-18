from tests.base_test import BaseTest
from arc.errors import ArcError
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

    def test_execute(self):
        self.cli("func1 x=2")
        self.cli.scripts["func1"].function.assert_called_with(x="2")

        self.cli("func2 x=2")
        self.cli.scripts["func2"].function.assert_called_with(x=2)

    def test_nonexistant_utility(self):
        with self.assertRaises(ArcError):
            self.cli("doesnotexist:func1 x=2")
