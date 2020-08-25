import unittest
from unittest.mock import create_autospec
from arc import CLI, Utility


# pylint: disable=protected-access, missing-function-docstring
class BaseTest(unittest.TestCase):
    scripts = [
        dict(name="func1", function=lambda x: x, annotations={}),
        dict(name="func2", function=lambda x: x, annotations={"x": int}),
    ]

    def create_cli(self, utilities=list()):
        cli = CLI(utilities=utilities)
        for script in self.scripts:
            self.create_script(
                cli, script["name"], script["function"], script["annotations"]
            )

        return cli

    def create_util(self, name="util"):
        util = Utility(name=name)

        for script in self.scripts:
            self.create_script(
                util, script["name"], script["function"], script["annotations"]
            )

        return util

    def create_script(self, container, name, func, annotations=dict()):
        func.__annotations__ = annotations
        func = create_autospec(func)
        container.script(name=name)(func)
        return func
