import inspect
from typing import Dict, Any, List, Union, Tuple
from arc.errors import ScriptError

from arc.parser.data_types import ScriptNode, FlagNode, OptionNode
from .__option import Option, NO_DEFAULT
from .script import Script
from .__flag import Flag


class KeywordScript(Script):
    def __init__(self, name, function):
        self.pass_kwargs = False
        super().__init__(name, function)

    def execute(self, script_node: ScriptNode):
        args: Dict[str, Any] = {
            **{key: obj.value for key, obj in self.options.items()},
            **{key: obj.value for key, obj in self.flags.items()},
        }

        with self.catch():
            self.function(**args)

    def match_input(self, script_node: ScriptNode):
        self.__match_options(script_node.options)
        self.__match_flags(script_node.flags)

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

            if self.pass_kwargs and not option:
                self.options[node.name] = option = Option(
                    data_dict=dict(name=node.name, annotation=str, default=NO_DEFAULT)
                )
            elif not option:
                raise ScriptError(f"Option '{node.name}' not recognized")

            option.value = node.value
            option.convert()

        self.assert_options_filled()

    def __match_flags(self, flag_nodes: List[FlagNode]):
        """Get's the final flag values to pass to the script

        Compares the FlagNodes given with self.flags
        if they are present in both, the flag is set to True,
        if it is absent from the Nodes it is set to false

        :param flag_nodes: list of FlagNodes from the parser

        :raises ScriptError: if a flag is present in FlagNodes, but
        not in self.flags
        """
        for flag in flag_nodes:
            if flag.name in self.flags:
                self.flags[flag.name].reverse()
            else:
                raise ScriptError(f"Flag '{flag.name}' not recognized'")

    def build_args(self, function) -> Tuple[Dict[str, Option], Dict[str, Flag]]:
        sig = inspect.signature(function)
        options: Dict[str, Option] = {}
        flags: Dict[str, Flag] = {}

        for idx, param in enumerate(sig.parameters.values()):
            if param.annotation is bool:
                flags[param.name] = Flag(param)

            elif param.kind is param.VAR_POSITIONAL:
                raise ScriptError(
                    "Keyword Arc scripts do not allow *args.",
                    "If you wish to use it, add `positional=True`",
                    "to @cli.script. However, be aware that this will",
                    "make ALL options passed by position rather than keyword",
                )

            elif param.kind is param.VAR_KEYWORD:
                if idx != len(sig.parameters.values()) - 1:
                    raise ScriptError(
                        "The variable keyword arguement (**kwargs)",
                        "must be the last argument of the script",
                    )

                self.pass_kwargs = True

            else:
                options[param.name] = Option(param)

        return options, flags

    def validate_input(self, script_node: ScriptNode):
        if len(script_node.args) > 0:
            self.validation_errors.append(
                "This script accepts arguements by keyword"
                + " only. As a result, it will not accept input"
                + " in the form of 'value value value'"
            )
