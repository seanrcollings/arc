from arc.errors import ScriptError, ArcError, ExecutionError
from arc.config import Config
from arc.__option import Option


class Script:
    '''Each installed script will be an instances of this class

    :param name: Name to register the script under, used on the command lin
        to run the script
    :param options: available command lines options for the script. Passed in
        as a list of strings
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
        self.options = self.build_options(options)
        self.flags = self.build_flags(flags)

        if pass_kwargs and pass_args:
            raise ScriptError("pass_kwargs and pass_args cannot both be True")

        self.pass_args = pass_args
        self.pass_kwargs = pass_kwargs

        if (self.pass_args or self.pass_kwargs) and len(self.options) > 0:
            raise ScriptError("You cannot provide any options if",
                              "pass_args or pass_kwargs is set to True")

        if self.pass_args:
            method = "pass_args"
        elif self.pass_kwargs:
            method = "pass_kwargs"
        else:
            method = "standard"

        self.doc = "No Docstring"
        if self.function.__doc__ is not None:
            self.doc = self.function.__doc__.strip('\n\t ').replace(
                "\n", "\n\t")

    def __repr__(self):
        return f"<Script : {self.name}>"

    def __call__(self, user_input, before):
        '''External interface to execute a script
        :param user_input: list of user input obtained from sys.argv
        '''
        parsed_user_input = self.parse_user_input(user_input)

        if self.pass_args:
            # If pass_args is true, that means
            # that options will be a list of the
            # arguements to be passed to the function. Since
            # options is list, it needs to be unpacked
            # with one '*' instead of two
            self.function(*parsed_user_input["options"],
                          **parsed_user_input["flags"])
        else:
            self.function(**parsed_user_input["options"],
                          **parsed_user_input["flags"])

    ##################
    # PARSER METHODS #
    ##################
    def parse_user_input(self, user_input: list) -> dict:
        '''Converts command line arguements into python dictionary

        Dispatches both __parse_options and __parse_flags

        :param user_input: list of what the user typed in on the command line
        :returns: arguement dictionary to be unpacked with **
        '''

        flag_den = Config.flag_denoter

        options = filter(lambda x: not x.startswith(flag_den), user_input)
        flags = filter(lambda x: x.startswith(flag_den), user_input)
        parsed_flags = self.__parse_flags(flags)

        if self.pass_kwargs:
            parsed_options = dict(
                self.split(options, sep=Config.options_seperator))
            return {"options": parsed_options, "flags": parsed_flags}

        elif self.pass_args:
            return {"options": list(options), "flags": parsed_flags}

        else:
            parsed_options = self.__parse_options(options)
            return {"options": parsed_options, "flags": parsed_flags}

    def __parse_options(self, options):
        ''' Parses the options provided by the user

        Tries to convert the value with the associated converter
        Takes in Command line options, converts them
        to a dictionary of arguements that can be passed to
        the script function as kwargs

        :param options: list of strings that the user typed in
            Examples:
                - ["port=5000","config=dev"]
                The function parses these strings into key value pairs (key=value)
                It also attempts to convert them to the specified type
        '''
        parsed = {}

        for name, value in self.split(options, sep=Config.options_seperator):
            if name not in self.options.keys():
                raise ExecutionError(f"'{name}' option not recognized")

            name, value = self.options[name](value)

            parsed[name] = value

        return parsed

    def __parse_flags(self, flags):
        '''Checks if provided user flags exist
        Sets flags that are provided to true

        :param flags: list of strings that start with "--"

        if the flag isn't recognized an ExecutionError is raised

        :returns: dictionary of flag names, paired with
        either true or false. If the flag was in the flags variable,
        it is set to true, otherwise it is false
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
    @staticmethod
    def build_options(options: list) -> dict:
        '''Creates option objects'''
        if options is None:
            return {}

        built_options = {}
        for option in options:
            option_obj = Option(option)
            built_options[option_obj.name] = option_obj
        return built_options

    @staticmethod
    def build_flags(flags: list) -> dict:
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

    # Other Helper Methods
    @staticmethod
    def split(options: list, sep: str):
        '''Generator that splits strings based on a provided seperator'''

        for option in options:
            if sep not in option:
                raise ExecutionError("Options must be seperated",
                                     f"from their values by '{sep}'")
            if option.endswith(sep):
                raise ExecutionError("Options must be given a value")

            name, value = option.split(sep)
            yield (name, value)
