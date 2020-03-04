from arc.errors import ExecutionError, ArcError
from arc.converter import is_converter
from arc.config import Config


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
            options) if options is not None else []
        self.named_arguements = named_arguements

        self.doc = "No Docstring"
        if self.function.__doc__ is not None:
            self.doc = self.function.__doc__.strip('\n\t ').replace(
                "\n", "\n\t")

    def __repr__(self):
        return f"<Script : {self.name}>"

    def execute(self, context_manager, user_arguements):
        '''Executes the script's function with the correct paramaters

        :param context_manager: the context manager for this particular script
            If it's not none, it will create the managed resource, then pass it
            to the script as the first arguement

        :param user_arguements: list of user_arguements obtained from sys.argv
        '''
        if context_manager is None:
            if self.options is None:
                self.function()
            elif not self.named_arguements:
                self.function(*user_arguements)
            else:
                self.function(**self.__parse_arguements(user_arguements))
        else:
            with context_manager as managed_resourece:
                if self.options is None:
                    self.function(managed_resourece)
                elif not self.named_arguements:
                    self.function(managed_resourece, *user_arguements)
                else:
                    self.function(managed_resourece,
                                  **self.__parse_arguements(user_arguements))

    @staticmethod
    def __build_options(options: list) -> list:
        '''Parses provided options and builds into a dictionary.

        Checks for a type converter
        :param options - array of strings. Can have a converter
            associated with it.
            - without converter "normal_string"
            - with converter "<int:number>"
        :return - a new array of dictionaries of the parsed options
            each option looks like this:
                {"name": "number", "converter": IntConverter}
            StringConverter is default converter
        '''
        built_options = []
        for option in options:
            option_dict = {
                "name": option,
                "converter": Config.converters["str"]
            }
            # Checks for a converter, if one exists,
            # Parse the option and set name and converter
            # to the correct values
            if option.startswith("<") and option.endswith(">"):
                if not is_converter(option):
                    raise ArcError(
                        f"'{option}' does not conform to converter syntax")

                # turns "<convertername:varname>" into ["convertername", "varname"]
                converter, name = option.lstrip("<").rstrip(">").split(":")

                if converter not in Config.converters:
                    raise ArcError((f"'{converter}' is not a valid",
                                    f"conversion identifier"))

                option_dict["name"] = name
                option_dict["converter"] = Config.converters[converter]

            built_options.append(option_dict)

        return built_options

    def __parse_arguements(self, user_options: list) -> dict:
        ''' Converts command line arguements into python dictionary

        Tries to convert the value with the associated converter
        Takes in Command line options, converts them
        to a dictionary of arguements that can be passed to
        the script function as kwargs

            :param script: the script script being ran by the user
            :param options: list of strings that the user typed in
                Examples:
                 - ["port=5000","config=dev"]
                 The function parses these strings into key value pairs (key=value)
                 It also attempts to convert them to the specified type

            :returns: arguement dictionary to be unpacked with **
        '''
        sep = Config.options_seperator
        user_options_dict = {}

        for option in user_options:
            if sep not in option:
                raise ExecutionError((f"Options must be seperated"
                                      f"from their values by '{sep}'"))
            if option.endswith(sep):
                raise ExecutionError("Options must be given a value")

            name, value = option.split(sep)

            if name not in [option["name"] for option in self.options]:
                raise ExecutionError(f"'{name}' option not recognized")

            user_options_dict[name] = value

        arguements = {}
        for option in self.options:
            if option["name"] in user_options_dict.keys():
                arguements[option["name"]] = option["converter"](
                    user_options_dict[option["name"]])

        return arguements
