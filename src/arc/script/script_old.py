import sys
import inspect
from typing import List, Dict, Callable, Any, Tuple

from arc.errors import ScriptError, ExecutionError
from arc.script.__option import Option, NO_DEFAULT
from arc.script.__flag import Flag
import arc._utils as util


class Script:
    """Each script installed to a CLI or utility is an instance of this class

    :param name: Name to register the script under, used on the command line
        to run the script
    :param options: available command lines options for the script. Passed in
        as a list of strings. Can be given a type converter
    :param raw: Specifies whether or not to parse out the command line arguements,
        or simply pass them along to the script. Flags will still be interpreted as flags
    :param convert: Will instruct the script not to attempt any conversions of the given data
    :param meta: meta data that can be passed in in the @script decorator. If it is a function,
        it will be called and that functions return will be passed into self.function
    :param function: Script function to be called with the parse and converted options
    """

    def __init__(
        self,
        name: str,
        convert: bool = True,
        meta: Any = None,
        positional=False,
        *,
        function: Callable,
    ):

        self.name = name
        self.function: Callable = function
        self.convert = convert
        self.pass_kwargs = False
        self.pass_args = False
        self.positional = positional
        self.options, self.flags = self.__build_args(self.function)

        if callable(meta):
            self.meta = meta()
        else:
            self.meta = meta

        self.doc = "No Docstring"
        if self.function.__doc__ is not None:
            self.doc = self.function.__doc__.strip("\n\t ").replace("\n", "\n\t")

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def __call__(self, script_node):
        """External interface to execute a script"""

        # __match* methods mutate a state object with respect to the script_node
        # the mutated state object's values will then be passed on to the script
        if self.positional:
            self.__match_pos_options(script_node.args)
        else:
            self.__match_options(script_node.options)

        self.__match_flags(script_node.flags)

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

        if self.meta is not None:
            kwargs["meta"] = self.meta

        try:
            util.logger("---------------------------")
            self.function(*posargs, **kwargs)
            util.logger("---------------------------")
        except ExecutionError as e:
            print(e)
            sys.exit(1)

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

            if self.convert:
                self.options[option.name].convert()

        self.__options_filled()

    def __match_pos_options(self, arg_nodes: list):
        """Mutates self.options based on positional strings
        """
        length = len(arg_nodes)
        for idx, option in enumerate(self.options.values()):
            if len(arg_nodes) >= idx:
                option.value = arg_nodes.pop(0).value
                if self.convert:
                    option.convert()

        if len(arg_nodes) != 0 and not self.pass_args:
            raise ScriptError(
                f"Script recieved {length} arguments, expected {len(self.options)}"
            )

        self.__options_filled()

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

    def __build_args(self, func) -> Tuple[Dict[str, Option], Dict[str, Flag]]:
        sig = inspect.signature(func)
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

    # HELPERS
    def __options_filled(self):
        for option in self.options.values():
            if option.value is NO_DEFAULT:
                raise ScriptError(f"No valued for required option '{option.name}'")
