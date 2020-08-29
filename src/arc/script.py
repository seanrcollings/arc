import sys
import inspect
from typing import List, Dict, Callable, Any, Union, Tuple

from arc.errors import ScriptError, ExecutionError
from arc.__option import Option, NoDefault
import arc._utils as util


class Flag:
    def __init__(self, param):
        self.name = param.name
        if param.default is param.empty:
            self.value = False
        else:
            self.value = param.default


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
        self, name: str, convert: bool = True, meta: Any = None, *, function: Callable,
    ):

        self.name = name
        self.function: Callable = function
        self.convert = convert
        self.pass_kwargs = False
        self.pass_args = False
        self.options, self.flags = self.__build_args(self.function)

        if callable(meta):
            self.meta = meta()
        else:
            self.meta = meta

        self.doc = "No Docstring"
        if self.function.__doc__ is not None:
            self.doc = self.function.__doc__.strip("\n\t ").replace("\n", "\n\t")

    def __repr__(self):
        return f"<Script : {self.name}>"

    def __call__(self, script_node):
        """External interface to execute a script"""

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
        """Get's the final option values to pass to script
       iterates though the option_nodes and sets their values
       as the values to each Option object in self.options

       :param option_nodes: list of OptionNodes from the parser

       :raises ScriptError:
            - if a option is present in option_nodes and
            not in self.options
            - if a option is not given a value and does not
            have a default value provided by self.function
       """

        # Ideally these two loops could be consolidated
        # into a single loop and that would half the runtime
        # (O(2n) -> O(n)). But since the length of arrays is never
        # going to be a size where that would matter, it shouldn't
        # ever cause an issue. I pray for the soul who writes a script
        # with enough options where that would matter

        # Sets the value property on the each Option
        for option in option_nodes:
            if option.name not in self.options:
                if self.pass_kwargs:
                    self.options[option.name] = Option(
                        data_dict=dict(
                            name=option.name, annotation=str, default=NoDefault
                        )
                    )
                else:
                    raise ScriptError(f"Option '{option.name}' not recognized")

            self.options[option.name].value = option.value

            if self.convert:
                self.options[option.name].convert()

        for option in self.options.values():
            if option.value is NoDefault:
                raise ScriptError(f"No valued for required option '{option.name}'")

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
                self.flags[flag.name].value = not self.flags[flag.name].value
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
