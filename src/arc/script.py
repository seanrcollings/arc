from arc.errors import ExecutionError, ArcError
from arc.config import Config
from arc.__option import Option


class Script:
    '''Each installed script will be an instances of this class

    :param name: Name to register the script under, used on the command lin
        to run the script
    :param options: available command lines options for the script. Passed in
        as a list of strings, parsed into a dictionary by __build_options
    :param named_arguements: Specifies whether or not options require keywords
        True: All arguements require names, arguement that doesn't match
        the script's options will be ignored
        False: Arguements do not require names, all arguements will be
        passed to the script (*args)
    '''
    def __init__(self,
                 name: str,
                 function,
                 options: list = None,
                 flags: list = None,
                 named_arguements: bool = True):

        self.name = name
        self.function = function
        self.options = self.__build_options(options)
        self.flags = self.__build_flags(flags)

        self.named_arguements = named_arguements

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
        self.execute(user_input, before)

    def execute(self, user_input, before):
        '''Executes the script's function with the correct paramaters

        :param user_input: list of user input obtained from sys.argv
        '''
        parsed_user_input = self.__parse_user_input(user_input)

        if self.options is None:
            self.function()
        elif not self.named_arguements:
            self.function(*user_input)
        else:
            self.function(**parsed_user_input)

    @staticmethod
    def __build_options(options: list) -> dict:
        '''Creates option objects'''
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

    def __parse_user_input(self, user_input: list) -> dict:
        '''Converts command line arguements into python dictionary

        Dispatches both __parse_options and __parse_flags

        :param user_input: list of what the user typed in on the command line
        :returns: arguement dictionary to be unpacked with **
        '''
        flag_den = Config.flag_denoter

        options = filter(lambda x: not x.startswith(flag_den), user_input)
        parsed_options = self.__parse_options(options)

        flags = filter(lambda x: x.startswith(flag_den), user_input)
        parsed_flags = self.__parse_flags(flags)

        return {**parsed_options, **parsed_flags}

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
        sep = Config.options_seperator
        for option in options:
            if sep not in option:
                raise ExecutionError("Options must be seperated",
                                     f"from their values by '{sep}'")
            if option.endswith(sep):
                raise ExecutionError("Options must be given a value")

            name, value = option.split(sep)

            if name not in self.options.keys():
                raise ExecutionError(f"'{name}' option not recognized")

            name, value = self.options[name](value)
            parsed[name] = value

        return parsed

    def __parse_flags(self, flags):
        '''Checks if provided user flags exist
        Sets flags that are provided to true

        if the flag isn't recognized an ExecutionError is raised
        '''
        flags_copy = self.flags.copy()
        for flag in flags:
            flag = flag.lstrip(Config.flag_denoter)
            if flag in flags_copy:
                flags_copy[flag] = not flags_copy[flag]
            else:
                raise ExecutionError(f"Flag '{flag}' not recognized")
        return flags_copy
