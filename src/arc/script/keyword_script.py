from typing import Any, Dict, List, Union

from arc import utils
from arc.errors import ScriptError, ValidationError
from arc.parser.data_types import OptionNode, ScriptNode

from .__option import NO_DEFAULT, Option
from .script import Script
from .script_mixin import ScriptMixin


class KeywordScript(Script, ScriptMixin):
    def __init__(self, name, function, *args, **kwargs):
        self.__pass_kwargs = False
        super().__init__(name, function, *args, **kwargs)

    def execute(self, script_node: ScriptNode):
        args: Dict[str, Any] = {
            **{key: obj.value for key, obj in self.options.items()},
            **{key: obj.value for key, obj in self.flags.items()},
        }

        self.function(**args)

    def match_input(self, script_node: ScriptNode):
        self.__match_options(script_node.options)
        self._match_flags(script_node.flags)

    def __match_options(self, option_nodes: List[OptionNode]):
        """Mutates self.options based on key value pairs provided in
         option nodes

        :param option_nodes: list of OptionNodes from the parser

        :raises ScriptError:
             - if a option is present in option_nodes and
             not in self.options
        """

        for node in option_nodes:
            option: Union[Option, None] = self.options.get(node.name)

            if self.__pass_kwargs and not option:
                self.options[node.name] = option = Option(
                    name=node.name, annotation=str, default=NO_DEFAULT
                )
            elif not option:
                raise ScriptError(f"Option '{node.name}' not recognized")

            option.value = node.value
            option.convert()

        self.add_meta()
        self.assert_options_filled()

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

    def validate_input(self, script_node: ScriptNode):
        if len(script_node.args) > 0:
            raise ValidationError(
                "This script accepts arguements by keyword"
                + " only. As a result, it will not accept input"
                + " in the form of 'value value value'"
            )
