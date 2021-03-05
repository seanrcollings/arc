import sys

from arc.parser.data_types import CommandNode
from .command import Command


class RawCommand(Command):
    def execute(self, _command_node: CommandNode):
        self.function(
            *sys.argv, {obj.name: obj.value for obj in self.hidden_args.values()}
        )

    def match_input(self, _command_node: CommandNode):
        ...
