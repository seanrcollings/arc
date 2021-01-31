import sys

from arc.parser.data_types import CommandNode
from .script import Script


class RawScript(Script):
    def execute(self, command_node):
        with self.catch():
            if self.meta:
                self.function(*sys.argv, meta=self.meta)
            else:
                self.function(*sys.argv)

    def match_input(self, command_node: CommandNode):
        ...
