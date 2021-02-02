from typing import List, Any

from arc.parser.data_types import ScriptNode, ArgNode
from arc.errors import ScriptError, ValidationError

from .script import Script
from .script_mixin import ScriptMixin


class PositionalScript(Script, ScriptMixin):
    def __init__(self, *args, **kwargs):
        self.__pass_args = False
        super().__init__(*args, **kwargs)

    def execute(self, script_node: ScriptNode):
        args: List[Any] = [
            *[obj.value for obj in self.options.values()],
            *[obj.value for obj in self.flags.values()],
        ]

        if self.__pass_args:
            args += [arg.value for arg in script_node.args]

        self.function(*args)

    def match_input(self, script_node: ScriptNode):
        self.__match_options(script_node.args)
        self._match_flags(script_node.flags)

    def __match_options(self, arg_nodes: List[ArgNode]):
        options = list(self.options.values())

        for option in options:
            if len(arg_nodes) == 0:
                break
            option.value = arg_nodes.pop(0).value
            option.convert()

        self.add_meta()
        self.assert_options_filled()

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

    def validate_input(self, script_node: ScriptNode):
        if len(script_node.options) > 0:
            raise ValidationError(
                "This script accepts arguements by position",
                "only. As a result, it will not accept input",
                "in the form of 'option=value'",
            )

        if len(script_node.args) > len(self.options) and not self.__pass_args:
            raise ValidationError(
                "You passed more arguments than this script accepts.",
                f"accepts: {self.options} | got:{len(script_node.args)}",
            )
