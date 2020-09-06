from typing import List, Dict, Tuple, Any
import inspect

from arc.parser.data_types import ScriptNode, FlagNode, ArgNode
from arc.errors import ScriptError
from .script import Script
from .__option import Option
from .__flag import Flag


class PositionalScript(Script):
    def __init__(self, *args, **kwargs):
        self.pass_args = False
        super().__init__(*args, **kwargs)

    def execute(self, script_node: ScriptNode):
        self.match_input(script_node)

        args: List[Any] = [
            *[obj.value for obj in self.options.values()],
            *[obj.value for obj in self.flags.values()],
        ]

        if self.pass_args:
            args += script_node.args

        with self.catch():
            self.function(*args)

    def match_input(self, script_node: ScriptNode):
        self.__match_options(script_node.args)
        self.__match_flags(script_node.flags)

    def __match_options(self, arg_nodes: List[ArgNode]):
        options = list(self.options.values())
        if len(arg_nodes) < len(options):
            raise ScriptError(
                "Script failed to recieve values for options:",
                ", ".join([option.name for option in options[len(arg_nodes) :]]),
            )

        for option in options:
            option.value = arg_nodes.pop(0).value
            option.convert()

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
                continue

            if param.kind is param.VAR_KEYWORD:
                raise ScriptError(
                    "Positional Arc scripts do not allow **kwargs.",
                    "If you wish to use it, remove `positional=True`",
                    "from @cli.script. However, be aware that this will",
                    "make ALL options passed by keyword rather than position",
                )

            if param.kind is param.VAR_POSITIONAL:
                if idx != len(sig.parameters.values()) - 1:
                    raise ScriptError(
                        "The variable postional arguement (*args)",
                        "must be the last argument of the script",
                    )

                self.pass_args = True

            else:
                options[param.name] = Option(param)

        return options, flags
