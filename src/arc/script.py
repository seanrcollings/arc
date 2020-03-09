from pprint import pformat, pprint
from arc.errors import ScriptError, ArcError, ExecutionError
from arc.config import Config
from arc.__option import Option
from arc._utils import logger


class Script:
    '''Each script installed to a CLI or utility is an instance of this class

    :param name: Name to register the script under, used on the command line
        to run the script
    :param options: available command lines options for the script. Passed in
        as a list of strings. Can be given a type converter
    :param pass_args: Specifies whether or not to parse out the command line arguements,
        or simply pass them along to the script. Flags will still be interpreted as flags
    :param pass_kwargs: Similar to pass_args, but will parse the args into a dictionary,
        splitting on the Config.options_seperator. Flags will still be interpreted as flags
    '''
    def __init__(self,
                 name: str,
                 function,
                 options: list = None,
                 flags: list = None,
                 pass_args: bool = False,
                 pass_kwargs: bool = False):

        self.name = name
        self.function = function
        self.options = self.__build_options(options)
        self.flags = self.__build_flags(flags)

        if pass_kwargs and pass_args:
            raise ScriptError("pass_kwargs and pass_args cannot both be True")

        self.pass_args = pass_args
        self.pass_kwargs = pass_kwargs

        if (self.pass_args or self.pass_kwargs) and len(self.options) > 0:
            raise ScriptError("You cannot provide any options if",
                              "pass_args or pass_kwargs is set to True")

        self.doc = "No Docstring"
        if self.function.__doc__ is not None:
            self.doc = self.function.__doc__.strip('\n\t ').replace(
                "\n", "\n\t")

    def __repr__(self):
        return f"<Script : {self.name}>"

    def __call__(self, user_input: list):
        '''External interface to execute a script
        :param user_input: list of user input obtained from sys.argv
        '''
        parsed_user_input = self.__parse_user_input(user_input)
        logger("Parsed script arguements:", level=3, state="info")
        logger(pformat(parsed_user_input, indent=4), level=3, state="info")

        if self.pass_args:
            # If pass_args is true, that means
            # that options will be a list of the
            # arguements to be passed to the function. Since
            # options is list, it needs to be unpacked
            # with one '*' instead of two
            self.function(*parsed_user_input["options"],
                          **parsed_user_input["flags"])
        else:
            # if pass_args is false, that means
            # that options will be a dictionary
            # to be unpacked with ** and passed
            # to the function as key word arguements
            self.function(**parsed_user_input["options"],
                          **parsed_user_input["flags"])

    ##################
    # PARSER METHODS #
    ##################
    def __parse_user_input(self, user_input: list) -> dict:
        '''Converts command line arguements into python dictionary

        :param user_input: list of what the user typed in on the command line
            The user's input need to parsed into both options (option=value)
            and flags (--reverse). Once these two are filtered out from each other,
            both __parse_options and __parse_flags are dispatched. These handle the
            checking if the provided values are valid for this particular script.

            The manner in which options are parsed is based on pass_args and pass_kwargs
            instance variables

                By default (pass_kwargs & pass_args == False), options are parsed
                by splittingon the Config.options_seperator, then checking if it is
                a valid option registered to the script. If it is, then it will attempt
                to convert the value via it's type converter.

                If pass_kwargs is True, options will be split on the Config.options_seperator
                ('=' by default) and those will be passed to the script.

                If pass_args is True, options will just be returned as the filtered list of
                arguements passed to it

            Flags are always parsed the same

        :returns: arguement dictionary to be unpacked with **
        '''

        flag_den = Config.flag_denoter

        options = filter(lambda x: not x.startswith(flag_den), user_input)
        flags = filter(lambda x: x.startswith(flag_den), user_input)
        parsed_flags = self.__parse_flags(flags)

        if self.pass_kwargs:
            parsed_options = dict(
                self.__split(options, sep=Config.options_seperator))
            return {"options": parsed_options, "flags": parsed_flags}

        elif self.pass_args:
            return {"options": list(options), "flags": parsed_flags}

        else:
            parsed_options = self.__parse_options(options)
            return {"options": parsed_options, "flags": parsed_flags}

    def __parse_options(self, options: list) -> dict:
        ''' Parses the options provided by the user

        :param options: list of strings that the user typed in
            Tries to convert the value with the associated converter
            Takes in Command line options, converts them
            to a dictionary of arguements that can be passed to
            the script function as kwargs

        :returns: dictionary of parsed and converted values

        :raises ExecutionError: if an option is not in self.options

        :example:
            register: @cli.script("example", options=["name", "<int:number>"], flags=["--reverse"])
            User enters: python3 example.py example name=Joseph number=2 --reverse
            Method recieves: ["name=Joseph", "number=2"]
            Method returns: {"name": "Joseph", "number": 2}
        '''
        parsed = {}

        for name, value in self.__split(options, sep=Config.options_seperator):
            if name not in self.options.keys():
                raise ExecutionError(f"'{name}' option not recognized")

            name, value = self.options[name](value)

            parsed[name] = value

        return parsed

    def __parse_flags(self, flags: list) -> dict:
        '''Checks if provided user flags exist
        Sets flags that are provided to true

        :param flags: list of flags to be parsed
            If a flag is present in the user input and
            in the script's flags, that flag's value is
            set to True. Otherwise, it is set to false

        :returns: a copy of self.flags with the boolean
        values swapped based on provided user flags

        :raises ExecutionError: if a flag is not in self.flags

        :example:
            register: @cli.script("example", options=["name", "<int:number>"], flags=["--reverse"])

            User enters: python3 example.py example name=Joseph number=2 --reverse
            Method recieves: ["--reverse"]
            Method returns: {"reverse": True}

            User enters: python3 example.py example name=Joseph number=2
            Method recieves: []
            Method returns: {"reverse": False}
        '''
        flags_copy = self.flags.copy()
        for flag in flags:
            flag = flag.lstrip(Config.flag_denoter)
            if flag in flags_copy:
                flags_copy[flag] = not flags_copy[flag]
            else:
                raise ExecutionError(f"Flag '{flag}' not recognized")
        return flags_copy

    ###################
    # BUILDER METHODS #
    ###################
    # The build methods are used on intial construction of a CLI
    # Each script installed must parse it's given options, flags and the like
    # to determine the user's intent. If something about the syntax is wrong,
    # always attempt to raise a ArcError with a helpful error message so the
    # user knows what they did wrong
    @staticmethod
    def __build_options(options: list) -> dict:
        '''Creates option objects

        :param options: list of user provided options. May contain a type converter
        :returns: dictionary of name keys and Option object values
        '''
        if options is None:
            return {}

        built_options = {}
        for option in options:
            option_obj = Option(option)
            built_options[option_obj.name] = option_obj
        return built_options

    @staticmethod
    def __build_flags(flags: list) -> dict:
        '''Insures flags follow specific standards
            :param flags: list of all flags registered to the scriot

            :returns: dictionary of flag names paired with a default False value
        '''
        if flags is None:
            return {}

        built_flags = {}
        for flag in flags:
            if not flag.startswith(Config.flag_denoter):
                raise ArcError(
                    "Flags must start with the denoter",
                    f"'{Config.flag_denoter}'",
                    "\nThis denoter can be changed by editing 'Config.flag_denoter'"
                )
            built_flags[flag.lstrip(Config.flag_denoter)] = False

        return built_flags

    # Helper Methods
    @staticmethod
    def __split(items: list, sep: str):
        '''Generator that splits strings based on a provided seperator

        :param items: list of strings to be split
        :param sep: string to split each item in items on

        :yields: tuple of the thing left and right of the seperator

        :raises ExecutionError: item does not contain the seperator
        :raises ExecutionError: if nothing is to the right or lef
            of the seperator
        '''

        for item in items:
            if sep not in item:
                raise ExecutionError("Options must be seperated",
                                     f"from their values by '{sep}'")
            if item.endswith(sep):
                raise ExecutionError("Options cannot begin or ",
                                     f"end with '{sep}'")

            name, value = item.split(sep)
            yield (name, value)
