from arc.errors import ExecutionError
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
                 named_arguements: bool = True):

        self.name = name
        self.function = function
        self.options = self.__build_options(
            options) if options is not None else {}
        self.named_arguements = named_arguements

        self.doc = "No Docstring"
        if self.function.__doc__ is not None:
            self.doc = self.function.__doc__.strip('\n\t ').replace(
                "\n", "\n\t")

    def __repr__(self):
        return f"<Script : {self.name}>"

    def __call__(self, context_manager, user_options):
        '''External interface to execute a script

        :param context_manager: the context manager for this particular script
            If it's not none, it will create the managed resource, then pass it
            to the execute method as an arg
        '''
        if context_manager is None:
            self.execute(user_options)
        else:
            with context_manager(user_options.pop(0)) as managed_resourece:
                self.execute(user_options, managed_resourece)

    def execute(self, user_options, *args):
        '''Executes the script's function with the correct paramaters

        :param user_options: list of user input obtained from sys.argv
        :param args: list of arbitrary arguments to pass to a script
            All managed resources exist in this variable
            Consider also using this to pass arbitrary args and kwargs
            to the scripts
        '''
        if self.options is None:
            self.function(*args)
        elif not self.named_arguements:
            self.function(*args, *user_options)
        else:
            self.function(*args, **self.__parse_user_options(user_options))

    @staticmethod
    def __build_options(options: list) -> list:
        '''Creates option objects'''
        built_options = {}
        for option in options:
            option_obj = Option(option)
            built_options[option_obj.name] = option_obj
        return built_options

    def __parse_user_options(self, user_options: list) -> dict:
        '''Converts command line arguements into python dictionary

        Tries to convert the value with the associated converter
        Takes in Command line options, converts them
        to a dictionary of arguements that can be passed to
        the script function as kwargs

        :param options: list of strings that the user typed in
            Examples:
                - ["port=5000","config=dev"]
                The function parses these strings into key value pairs (key=value)
                It also attempts to convert them to the specified type

        :returns: arguement dictionary to be unpacked with **
        '''
        sep = Config.options_seperator
        arguements = {}

        for option in user_options:
            if sep not in option:
                raise ExecutionError("Options must be seperated",
                                     f"from their values by '{sep}'")
            if option.endswith(sep):
                raise ExecutionError("Options must be given a value")

            name, value = option.split(sep)

            if name not in self.options.keys():
                raise ExecutionError(f"'{name}' option not recognized")

            name, value = self.options[name](value)
            arguements[name] = value

        return arguements
