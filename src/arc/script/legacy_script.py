import inspect
from typing import List, Dict, Any, Tuple

from arc.errors import ScriptError
from arc.script.__option import Option, NO_DEFAULT
from arc.script.__flag import Flag
from arc.parser.data_types import ScriptNode
from .script import Script


class LegacyScript(Script):
    """Legacy Script behavior, not reccomended"""

    def __init__(self, *args, positional=False, convert=False, **kwargs):
        self.positional = positional
        self.pass_kwargs = False
        self.pass_args = False
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def execute(self, script_node):
        """External interface to execute a script"""

        kwargs: Dict[str, Any] = {
            **{key: obj.value for key, obj in self.options.items()},
            **{key: obj.value for key, obj in self.flags.items()},
        }
        posargs: List[str] = [a.value for a in script_node.args]

        if len(posargs) > 0 and not self.pass_args:
            raise ScriptError(
                "Cannot pass artibrary arguements when there is no",
                "*args specified in script definition",
            )

        with self.catch():
            self.function(*posargs, **kwargs)

    def match_input(self, script_node: ScriptNode):
        # __match* methods mutate a state object with respect to the script_node
        # the mutated state object's values will then be passed on to the script
        if self.positional:
            self.__match_pos_options(script_node.args)
        else:
            self.__match_options(script_node.options)

        self.__match_flags(script_node.flags)

    def __match_options(self, option_nodes: list):
        """Mutates self.options based on key value pairs provided in
        option nodes

       :param option_nodes: list of OptionNodes from the parser

       :raises ScriptError:
            - if a option is present in option_nodes and
            not in self.options
            - if a option is not given a value and does not
            have a default value provided by self.function
       """

        for option in option_nodes:
            if option.name not in self.options:
                if self.pass_kwargs:
                    self.options[option.name] = Option(
                        data_dict=dict(
                            name=option.name, annotation=str, default=NO_DEFAULT
                        )
                    )
                else:
                    raise ScriptError(f"Option '{option.name}' not recognized")

            self.options[option.name].value = option.value
            self.options[option.name].convert()

        self.assert_options_filled()

    def __match_pos_options(self, arg_nodes: list):
        """Mutates self.options based on positional strings
        """
        length = len(arg_nodes)
        for idx, option in enumerate(self.options.values()):
            if len(arg_nodes) >= idx:
                option.value = arg_nodes.pop(0).value
                option.convert()

        if len(arg_nodes) != 0 and not self.pass_args:
            raise ScriptError(
                f"Script recieved {length} arguments, expected {len(self.options)}"
            )

        self.assert_options_filled()

    def __match_flags(self, flag_nodes: list):
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

            elif param.kind is param.VAR_KEYWORD:
                if idx != len(sig.parameters.values()) - 1:
                    raise ScriptError(
                        "**kwargs must be the last argument of the script"
                    )
                self.pass_kwargs = True

            elif param.kind is param.VAR_POSITIONAL:
                if idx != 0:
                    raise ScriptError("*args must be the first argument of the script")
                self.pass_args = True

            else:
                options[param.name] = Option(param)

        return options, flags
