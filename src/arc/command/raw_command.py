import sys

from arc.parser.data_types import CommandNode
from .command import Command


class RawCommand(Command):
    def execute(self, _command_node: CommandNode):
        if self.meta:
            self.function(*sys.argv, meta=self.meta)
        else:
            self.function(*sys.argv)

    def match_input(self, _command_node: CommandNode):
        ...
