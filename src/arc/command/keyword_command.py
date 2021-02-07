from typing import Any, Dict, List, Union, cast

from arc.errors import ScriptError, ValidationError
from arc.parser.data_types import FLAG, POS_ARGUMENT, ArgNode, CommandNode

from .__option import NO_DEFAULT, Option
from .command import Command
from .script_mixin import ScriptMixin


class KeywordCommand(Command, ScriptMixin):
    def __init__(self, name, function, *args, **kwargs):
        self.__pass_kwargs = False
        super().__init__(name, function, *args, **kwargs)

    def execute(self, command_node: CommandNode):
        args: Dict[str, Any] = {key: obj.value for key, obj in self.args.items()}

        self.function(**args)

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
            node.name = cast(str, node.name)
            option: Union[Option, None] = self.args.get(node.name)

            if self.__pass_kwargs and not option:
                self.args[node.name] = option = Option(
                    name=node.name, annotation=str, default=NO_DEFAULT
                )
            elif not option:
                raise ScriptError(f"Option '{node.name}' not recognized")

            if node.kind is FLAG:
                option.value = not option.value
            else:
                option.value = node.value
                option.convert()

        self.add_meta()
        self.assert_args_filled()

    def arg_hook(self, param, meta):
        idx = meta["index"]

        if param.kind is param.VAR_POSITIONAL:
            raise ScriptError(
                "Keyword Arc scripts do not allow *args.",
                "If you wish to use it, change the script type to POSITIONAL",
                "However, be aware that this will",
                "make ALL options passed by position rather than keyword",
            )

        if param.kind is param.VAR_KEYWORD:
            if idx != meta["length"] - 1:
                raise ScriptError(
                    "The variable keyword arguement (**kwargs)",
                    "must be the last argument of the script",
                )

            self.__pass_kwargs = True

    def validate_input(self, command_node: CommandNode):
        for node in command_node.args:
            if node.kind is POS_ARGUMENT:
                raise ValidationError(
                    "This script accepts arguements by keyword"
                    " only. As a result, it will not accept input"
                    " in the form of 'key=value key=value key=value'"
                )
