import sys
import re

from arc.config import Config
from arc.converter import ConversionError


class CLI:
    config = Config

    def __init__(self, utilities: list = None, context_manager=None):
        self.scripts = {}
        self._install_script(function=self.helper,
                             name="help",
                             options=None,
                             named_arguements=True)
        self.context_manager = context_manager

        if self.__class__ is CLI:
            self.utilities = {}
            if utilities is not None:
                self.install_utilities(*utilities)

    def __call__(self):
        if len(sys.argv) < 2:
            print("You didn't provide any options.",
                  "Check 'help' for more information")
            return

        utility, command = self.__parse_command(sys.argv[1])
        options = sys.argv[2:]

        if utility is not None:
            if utility not in self.utilities:
                print("That command does not exist")
                return

            self.utilities[utility](command, options)
        else:
            self._execute(command, options)

    def _execute(self, command: str, options: list):
        '''
        Executes the script from the user's command
            :param command - the user typed in i.e: server:run
            :param options - various options that the user passed in i.e: port=4321

        '''
        if command not in self.scripts:
            print("That command does not exist")
            return

        try:
            if self.context_manager is None:
                script: dict = self.scripts[command]
                if script['options'] is None:
                    self.scripts[command]['function']()
                elif not script['named_arguements']:
                    self.scripts[command]['function'](*options)
                else:
                    self.scripts[command]['function'](
                        **self.__arguements_dict(script, options))
            else:
                with self.context_manager as managed_resource:
                    script = self.scripts[command]
                    if script['options'] is None:
                        self.scripts[command]['function'](managed_resource)
                    if not script['named_arguements']:
                        self.scripts[command]['function'](managed_resource,
                                                          *options)
                    else:
                        self.scripts[command]['function'](
                            managed_resource,
                            **self.__arguements_dict(script, options))
        except TypeError as error:
            print(error)
            sys.exit(1)

    def script(self,
               name: str,
               options: list = None,
               named_arguements: bool = True):
        '''
        Decorator for registering a Script
        :param name: Name to register the script under, used on the command lin
        to run the script
        :param options: available command lines options for the script
        :named_arguements: Specifies whether or not options require keywords
            True: All arguements require names, arguement that doesn't match
            the script's options will be ignored
            False: Arguements do not require names, all arguements will be
            passed to the script (*args)

        '''
        def decorator(function):
            self._install_script(function, name, options, named_arguements)

        return decorator

    def _install_script(self, function, name, options, named_arguements):
        parsed_options = self.__build_options(options)
        self.scripts[name] = {
            'function': function,
            'options': parsed_options,
            'named_arguements': named_arguements
        }

    def install_utilities(self, *utilities):
        '''Installs a series of utilities to the CLI'''
        for utility in utilities:
            if repr(utility) == "Utility":  # work around for circular import
                self.utilities[utility.name] = utility
            else:
                print("Only instances of the 'Utility'",
                      "class can be registerd to Arc")
                sys.exit(1)

    @staticmethod
    def __arguements_dict(script: str, options: list) -> list:
        '''
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
        arguements = {}
        for option in options:
            switch, value = "", ""
            # TODO: Change around this try / except block
            try:
                switch, value = option.split("=")
            except ValueError:
                print("\033[1;41m   Options must be given a value,",
                      "ignoring....  \033[00m")
                break
            if switch in [option["name"] for option in script['options']]:
                converter = list(
                    filter(lambda option: option["name"] == switch,
                           script['options']))[0]["converter"]

                value = converter(value)

                arguements[switch] = value

        return arguements

    @staticmethod
    def __parse_command(command: str):
        if ":" in command:
            utility, command = command.split(":")
        else:
            utility = None

        return utility, command

    def __build_options(self, options: list):
        '''
        Parses provided options and builds
        into a dictionary. Checks for a type converter
        :param options - array of strings. Can have a converter
            associated with it.
            - without converter "normal_string"
            - with converter "<int:number>
        :return - a new array of dictionaries of the parsed options
            each option looks like this:
                {
                    "name": "number"
                    "converter": IntConverter
                }
            StringConverter is default converter
        '''
        built = []
        if options is not None:
            for option in options:
                option_dict = {
                    "name": option,
                    "converter": self.config.converters["str"]
                }
                # Matches to "<convertername:varname>""
                match = re.search("<.*:.*>", option)
                if match is not None:
                    # turns "<convertername:varname>" into ["convertername", "varname"]
                    converter, name = option.lstrip("<").rstrip(">").split(":")

                    if converter in self.config.converters:
                        option_dict["name"], option_dict[
                            "converter"] = name, self.config.converters[
                                converter]
                    else:
                        raise ConversionError(f"'{converter}' is not a valid",
                                              "conversion identifier")

                built.append(option_dict)

        return built

    def helper(self):
        '''
        Helper List function
        Prints out the docstrings for the clis's scripts
        '''
        print("Usage: python3 FILENAME [COMMAND] [ARGUEMENTS ...]\n")

        print("Possible Options: ")
        if len(self.scripts) > 0:
            for script, value in self.scripts.items():
                helper_text = "No Docstring"
                doc = value['function'].__doc__
                if doc is not None:
                    helper_text = doc.strip('\n\t ')

                print(f"\033[92m{script}\033[00m\n    {helper_text}\n")

        else:
            print("No scripts defined")

        if len(self.utilities) > 0:
            print("\nInstalled Utilities")
            for _, utility in self.utilities.items():
                utility.helper()
