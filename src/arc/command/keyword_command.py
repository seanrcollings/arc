from typing import Any, Dict, List, Union, cast

from arc.errors import CommandError, ValidationError
from arc.parser.data_types import FLAG, POS_ARGUMENT, ArgNode, CommandNode

from .__option import NO_DEFAULT, Option
from .command import Command
from .helpers import CommandMixin


class KeywordCommand(Command, CommandMixin):
    def __init__(self, name, function, *args, **kwargs):
        self.__pass_kwargs = False
        super().__init__(name, function, *args, **kwargs)

    def execute(self, command_node: CommandNode):
        args: Dict[str, Any] = {key: obj.value for key, obj in self.args.items()}
        return self.function(**args)

    def match_input(self, command_node: CommandNode):
        self.__match_options(command_node.args)

    def __match_options(self, option_nodes: List[ArgNode]):
        """Mutates self.args based on key value pairs provided in
         option nodes

        :param option_nodes: list of ArgNodes from the parser

        :raises ScriptError: if a option is present in option_nodes and
        not in self.args
        """
        for node in option_nodes:
            name = cast(str, node.name)
            option: Union[Option, None] = self.args.get(name)

            if self.__pass_kwargs and not option:
                self.args[name] = option = Option(
                    name=name, annotation=str, default=NO_DEFAULT
                )
            elif not option:
                raise CommandError(f"Option '{name}' not recognized")

            if node.kind is FLAG:
                option.value = not option.default
            else:
                option.value = node.value
                option.convert()

        self.assert_args_filled()

    def arg_hook(self, param, meta):
        idx = meta["index"]

        if param.kind is param.VAR_POSITIONAL:
            raise CommandError(
                "Keyword Arc scripts do not allow *args.",
                "If you wish to use it, change the command type to POSITIONAL",
                "However, be aware that this will",
                "make ALL options passed by position rather than keyword",
            )

        if param.kind is param.VAR_KEYWORD:
            if idx != meta["length"] - 1:
                raise CommandError(
                    "The variable keyword argument (**kwargs)",
                    "must be the last argument of the command",
                )

            self.__pass_kwargs = True

    def validate_input(self, command_node: CommandNode):
        for node in command_node.args:
            if node.kind is POS_ARGUMENT:
                raise ValidationError(
                    "This command is configured to"
                    " only accept arguments by keyword.\n"
                    f"You passed in '{node}' "
                    f"instead, pass in: 'arg_name={node}'\n"
                    "check 'help' for possible arguments"
                )
