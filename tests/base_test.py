import unittest

from arc import CLI, Utility


#pylint: disable=protected-access, missing-function-docstring
class BaseTest(unittest.TestCase):
    scripts = [
        dict(name="func1",
             function=lambda x: print(x),
             options=["x"],
             named_arguements=True),
        dict(name="func2",
             function=lambda x: print(int(x)**2),
             options=["x"],
             named_arguements=True)
    ]

    def create_cli(self, utilities=[]):
        cli = CLI(utilities=utilities)
        for script in self.scripts:
            cli._install_script(**script)

        return cli

    def create_util(self, name="util"):
        util = Utility(name=name)

        for script in self.scripts:
            util._install_script(**script)

        return util
