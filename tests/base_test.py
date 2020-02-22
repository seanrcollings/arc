import unittest
from arc import CLI


#pylint: disable=missing-function-docstring
class BaseTest(unittest.TestCase):
    def create_cli(self):
        cli = CLI()
        cli._install_script(name="func1",
                            function=lambda x: print(x),
                            options=["x"],
                            named_arguements=True)
        cli._install_script(name="func2",
                            function=lambda x: print(int(x)**2),
                            options=["x"],
                            named_arguements=True)

        return cli
