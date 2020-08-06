import unittest

from arc import CLI, Utility, Config

Config.debug = True
Config.log = True


# pylint: disable=protected-access, missing-function-docstring
class BaseTest(unittest.TestCase):
    scripts = [
        dict(name="func1", function=lambda x: print(x), options=["x"]),
        dict(name="func2", function=lambda x: print(int(x) ** 2), options=["x"]),
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
