import sys
import re
from cli.config import Config
from cli.converter import ConversionError
# sys.tracebacklimit = 0


class CLI:
    '''CLI Class Info Here'''
    config = Config

    def __init__(self, scripts={}, utilities=[], config=Config, context_manager=None):

        self.scripts = scripts
        self.scripts["help"] = {"function": self.helper, "options": None, "named_arguements": True}

        self.utilities = {}
        self.register_utilities(*utilities)

        self.context_manger = context_manager


    def __call__(self):
        if len(sys.argv) >= 2:
            self.__parse_command(sys.argv[1], sys.argv[2:])
        else:
            print("You didn't provide any options.",
                  "Check help for more information")

    def __parse_command(self, command, options):
        if ":" in command:
            utility, command = command.split(":")
        else:
            utility = None

        if utility is not None:
            if utility not in self.utilities:
                print("That command does not exist")
                return
            self.utilities[utility](command, options)
        else:
            self.execute(command, options)

    def execute(self, command, options):
        '''
        Executes the script from the user's command
            :param command - the user typed in i.e: server:run
            :param options - various options that the user passed in i.e: port=4321

        '''
        if command not in self.scripts:
            print("That command does not exist")
            return

        if self.context_manger is None:
            script = self.scripts[command]
            if script['options'] is None:
                self.scripts[command]['function']()
            if script['named_arguements'] == False:
                self.scripts[command]['function'](*options)
            else:
                self.scripts[command]['function'](
                    **self.arguements_dict(script, options))
        else:
            with self.context_manger as managed_resource:
                script = self.scripts[command]
                if script['options'] is None:
                    self.scripts[command]['function'](managed_resource)
                if script['named_arguements'] == False:
                    self.scripts[command]['function'](managed_resource, *options)
                else:
                    self.scripts[command]['function'](managed_resource,
                        **self.arguements_dict(script, options))

    def script(self, function_name, options=None, named_arguements=True):
        '''Decorator function to register a script'''
        def decorator(function):
            parsed_options = self.parse_options(options)
            self.scripts[function_name] = {
                'function': function,
                'options': parsed_options,
                'named_arguements': named_arguements
            }

        return decorator

    def register_utilities(self, *utilities):
        '''Registers a utility to the CLI'''
        for utility in utilities:
            if repr(utility) == "Utility":  # work around for circular import
                self.utilities[utility.name] = utility
            else:
                print("Only instances of the 'Utility'",
                    "class can be registerd to the CLi")
                sys.exit(1)

    # TODO: Rewrite
    def arguements_dict(self, script, options):
        '''
        Takes in Command line options, converts them
        to a dictionary of arguements that can be passed to
        the utility function as kwargs

            :param script - the utility script being rna by the user
            :param options - list of strings that the user typed in
                Examples:
                 - ["port=5000","config=dev"]
                 The function parses these strings into key value pairs (key=value)
                 It also attempts to convert them to the specified type

            :returns - arguement dictionary to be unpacked with **
        '''
        arguements = {}
        for option in options:
            switch, value = "", ""
            try:
                switch, value = option.split("=")
            except ValueError:
                print("\033[1;37;41m   Options must be given a value,",
                      "ignoring....  \033[0m")

            if switch in [option["name"] for option in script['options']]:
                converter = list(
                    filter(lambda option: option["name"] == switch,
                           script['options']))[0]["converter"]

                try:
                    value = converter(value)
                except ValueError:
                    print(f"'{value}' could not be converted",
                          f"to type '{converter.convert_to}'")
                    sys.exit(1)
                arguements[switch] = value

        return arguements

    # TODO: Rewrite
    def parse_options(self, options):
        '''
            Parses provided options, checking for a converter
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
        parsed = []
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
                        raise ConversionError(
                            f"'{converter}' is not a valid conversion identifier"
                        )

                parsed.append(option_dict)

        return parsed

    def helper(self):
        '''
        Helper List function
        '''
        print("Usage: python3 FILENAME [COMMAND] [ARGUEMENTS ...]\n")

        print("Possible Options: ")
        if len(self.scripts) > 0:
            for script, value in self.scripts.items():
                helper_text = "\tNo Docstring"
                if ( doc := value['function'].__doc__) is not None:
                    helper_text = doc.strip('\n')
                name = format(script)
                print(name)
                print(helper_text)
        else:
            print("No scripts defined")
        for name, utility in self.utilities.items():
            utility.helper()
