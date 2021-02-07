from typing import List, Any

from arc.parser.data_types import CommandNode, ArgNode, KEY_ARGUMENT, FLAG
from arc.errors import ScriptError, ValidationError

from .command import Command
from .command_mixin import CommandMixin


class PositionalCommand(Command, CommandMixin):
    def __init__(self, *args, **kwargs):
        self.__pass_args = False
        super().__init__(*args, **kwargs)

    def execute(self, command_node: CommandNode):
        args: List[Any] = [obj.value for obj in self.args.values()]

        if self.__pass_args:
            args += [arg.value for arg in command_node.args]

        self.function(*args)

    def match_input(self, command_node: CommandNode):
        self.__match_options(command_node.args)

    def __match_options(self, arg_nodes: List[ArgNode]):
        options = list(self.args.values())

        for option in options:
            if len(arg_nodes) == 0:
                break

            node = arg_nodes.pop(0)
            if node.kind is FLAG:
                option.value = not option.value
            else:
                option.value = node.value
                option.convert()

        self.add_meta()
        self.assert_args_filled()

    def arg_hook(self, param, meta):
        idx = meta["index"]

        if param.kind is param.VAR_KEYWORD:
            raise ScriptError(
                "Positional Arc scripts do not allow **kwargs.",
                "If you wish to use it, change the script type to KEYWORD",
                "in @cli.script. However, be aware that this will",
                "make ALL options passed by keyword rather than position",
            )

        if param.kind is param.VAR_POSITIONAL:
            if idx != meta["length"] - 1:
                raise ScriptError(
                    "The variable postional arguement (*args)",
                    "must be the last argument of the script",
                )

            self.__pass_args = True

    def validate_input(self, command_node: CommandNode):
        for node in command_node.args:
            if node.kind is KEY_ARGUMENT:
                raise ValidationError(
                    "This script accepts arguements by position"
                    "only. As a result, it will not accept input"
                    "in the form of 'option=value'"
                )

        if len(command_node.args) > len(self.args) and not self.__pass_args:
            raise ValidationError(
                "You passed more arguments than this script accepts.",
                f"accepts: {self.args} | got:{len(command_node.args)}",
            )
