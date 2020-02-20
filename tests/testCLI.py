import unittest
from unittest.mock import patch
from arc import CLI


class TestCLI(unittest.TestCase):
    def create_cli(self):
        scripts = {
            "func": {
                "function": lambda x: print(x),
                "options": ["x"],
                "named_arguements": True
            }
        }
        return CLI(scripts=scripts)

    def test_creation(self):
        cli = CLI()
        assert isinstance(cli, CLI)

    def test_adding_command(self):
        cli = self.create_cli()
        assert "func" in cli.scripts.keys()

    def test_run(self):
        cli = self.create_cli()
        with patch('sys.argv', ["garble", 'func', "x=2"]):
            cli()