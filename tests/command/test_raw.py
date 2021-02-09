from arc import run
from arc.command import RawCommand

from .base import BaseCommandTest


class TestRawCommand(BaseCommandTest):
    command_class = RawCommand

    def test_run(self):
        @self.command.subcommand()
        def raw(*args):
            ...

        run(self.command, "raw")
