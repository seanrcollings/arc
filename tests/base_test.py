import unittest
from unittest.mock import MagicMock
from arc import CLI, Utility, Config

Config.debug = True
Config.log = True


# pylint: disable=protected-access, missing-function-docstring
class BaseTest(unittest.TestCase):
    scripts = [
        dict(name="func1", function=MagicMock(), options=["x"]),
        dict(name="func2", function=MagicMock(), options=["<int:x>"]),
    ]

    def create_cli(self, utilities=[]):
        cli = CLI(utilities=utilities)
        for script in self.scripts:
            cli.script(name=script["name"], options=script["options"])(
                script["function"]
            )

        return cli

    def create_util(self, name="util"):
        util = Utility(name=name)

        for script in self.scripts:
            util.script(name=script["name"], options=script["options"])(
                script["function"]
            )

        return util
