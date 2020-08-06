import sys
import inspect
from typing import Optional, List, Dict, Callable
from arc.errors import ScriptError, ArcError
import arc._utils as util
from arc.config import Config
from arc.__option import Option


class Script:
    """Each script installed to a CLI or utility is an instance of this class

    :param name: Name to register the script under, used on the command line
        to run the script
    :param options: available command lines options for the script. Passed in
        as a list of strings. Can be given a type converter
    :param raw: Specifies whether or not to parse out the command line arguements,
        or simply pass them along to the script. Flags will still be interpreted as flags
    :param convert: Will instruct the script not to attempt any conversions of the given data
    """

    def __init__(
        self,
        name: str,
        function,
        options: List[str] = None,
        flags: List[str] = None,
        raw: bool = False,
        convert: bool = True,
    ):

        self.name = name
        self.function: Callable = function
        self.options: Dict[str, Option] = self.__build_options(options)
        self.flags: Dict[str, bool] = self.__build_flags(flags)
        self.raw = raw
        self.convert = convert

        self.doc = "No Docstring"
        if self.function.__doc__ is not None:
            self.doc = self.function.__doc__.strip("\n\t ").replace("\n", "\n\t")

    def __repr__(self):
        return f"<Script : {self.name}>"

    def __call__(self, options: list, flags: list):
        """External interface to execute a script"""

        self.__match_options(options)
        self.__match_flags(flags)

        util.logger("---------------------------")
        self.function(
            **{key: obj.value for key, obj in self.options.items()}, **self.flags
        )
        util.logger("---------------------------")

    def __match_options(self, option_nodes: list):
        """Get's the final option values to pass to script
       iterates though the option_nodes and sets their values
       as the values to each Option object in self.options

       :param option_nodes: list of OptionNodes from the parser

       :raises ScriptError: if a option is present in option_nodes and
       not in self.options
       :raises ScriptError: if a option is not given a value and does not
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
                raise ScriptError(f"Option '{option.name}' not recognized")

            self.options[option.name].value = option.value

            if self.convert:
                self.options[option.name].convert()

        # Iterates over the Option objects and checks if they have
        # a value propery set by the previous loop
        # if the option doesn't have a value, it checks
        # the functions' defaut value for that arguement
        # Default value is set as as the options value
        for name, option in self.options.items():
            if not hasattr(option, "value"):
                sig = inspect.signature(self.function)
                default = sig.parameters[name].default
                if default == sig.parameters[name].empty:
                    raise ScriptError(f"No value for required option: {name}")

                option.value = default

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
                self.flags[flag.name] = not self.flags[flag.name]
            else:
                raise ScriptError(f"Flag '{flag.name}' not recognized'")

    ###################
    # BUILDER METHODS #
    ###################
    # The build methods are used on intial construction of a CLI
    # Each script installed must parse it's given options, flags and the like
    # to determine the user's intent. If something about the syntax is wrong,
    # always attempt to raise a ArcError with a helpful error message so the
    # user knows what they did wrong
    @staticmethod
    def __build_options(options: Optional[List[str]]) -> Dict[str, Option]:
        """Creates option objects

        :param options: list of user provided options. May contain a type converter
        :returns: dictionary of name keys and Option object values
        """
        if options is None:
            return {}

        built_options = {}
        for option in options:
            option_obj = Option(option)
            built_options[option_obj.name] = option_obj
        return built_options

    @staticmethod
    def __build_flags(flags: Optional[List[str]]) -> Dict[str, bool]:
        """Insures flags follow specific standards
            :param flags: list of all flags registered to the scriot

            :returns: dictionary of flag names paired with a default False value
        """
        if flags is None:
            return {}

        built_flags = {}
        for flag in flags:
            if not flag.startswith(Config.flag_denoter):
                raise ArcError(
                    "Flags must start with the denoter",
                    f"'{Config.flag_denoter}'",
                    "\nThis denoter can be changed by editing 'Config.flag_denoter'",
                )
            built_flags[flag.lstrip(Config.flag_denoter)] = False

        return built_flags
