'''
Add the options to provide arbitrary arguements to a function with *args and **kwargs
Utility integrations
'''

import sys
from app.utils import parse_options


class CLI:
    '''CLI Class Info Here'''
    def __init__(self, scripts={}, utilities=[]):
        self.scripts = scripts
        self.register_script('help', self.helper, None)
        self.utilities = {}

        for utility in utilities:
            self.register_utility(utility)

    def __call__(self):
        if len(sys.argv) >= 2:
            self.__execute(sys.argv[1], sys.argv[2:])
        else:
            print("You didn't provide any options.",
                  "Check help for more information")

    def __execute(self, command, options):
        '''
        Executes the script from the user's command
            :param command - the user typed in i.e: server:run
            :param options - various options that the user passed in i.e: port=4321
        '''

        if ":" in command:
            utility, command = command.split(":")
            if utility in self.utilities:
                self.utilities[utility](command, options)
            else:
                print("That command does not exist")
            return

        if command not in self.scripts:
            print("That command does not exist")
            return

        script = self.scripts[command]
        if script['options'] is None:
            self.scripts[command]['function']()
        else:
            self.scripts[command]['function'](
                **self.arguements_dict(script, options))

    def script(self, function_name, options=None):
        '''Decorator function to register a script'''
        def decorator(function):
            self.register_script(function_name, function, options)

        return decorator

    def register_script(self, function_name, function, options):
        options = parse_options(options)
        self.scripts[function_name] = {
            'function': function,
            'options': options,
        }

    def register_utility(self, utility):
        '''Registers a utility to the CLI'''
        if repr(utility) == "Utility":
            self.utilities[utility.name] = utility
        else:
            print("Only instances of the 'Utility' class can be registerd to the CLi")
            sys.exit(1)

    def arguements_dict(self, script, options):
        '''
        Takes in Command line options, converts them
        to a dictionary of arguements that can be passed to
        the utility function as kwargs

            :param script - the utility script being rna by the user
            :param options - list of strings that the user typed in
                Examples:
                 - ["port=5000", "host=local", "config=dev"]
                 The function parses these strings into key value pairs (key=value)

            :returns - arguement dictionary
        '''
        arguements = {}
        for option in options:
            switch, value = "", ""
            try:
                switch, value = option.split("=")
            except ValueError:
                print("\033[1;37;41m   Options must be given a value,",
                      "ignoring....  \033[0m")

            if switch in [option["name"] for option in  script['options']]:
                converter = list(filter(lambda option: option["name"] ==
                    switch, script['options']))[0]["converter"]

                value = converter(value)
                arguements[switch] = value

        return arguements

    def helper(self):
        '''
        Helper function
        '''
        # print("Usage: python3 manage.py [COMMAND] [ARGUEMENTS ...]\n")
        print("Possible Options: ")
        for script, value in self.scripts.items():
            helper = doc.strip('\n') if ( doc := value['function'].__doc__) is not None else 'No docstring'
            name = format(script)
            print(name)
            print(helper)
        for name, utility in self.utilities.items():
            utility.helper()
