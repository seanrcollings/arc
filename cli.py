class CLI:
    '''
    Utility class for CLI
    Advantages of this new implementation:
        The naming of the commands is contained within that command's file
        I can have as many commands in one file as I want, and only have to import the file
        Allows me to be a bit more modular in the commands that I have,
        and where they are located and what they are called
    Disadvantages / Problems:
        I don't really like how the utility is called
        Requiring me to register every one of the utilites evertime that
        I want to run one of them seemes like unessecary overhead
    '''
    def __init__(self):
        self.scripts = {'help': {'function': self.helper, 'options': None}}

    def execute(self, command, options):
        '''
        Executes the script from the user's command
            :param command - the user typed in i.e: server:run
            :param options - various options that the user passed in i.e: port=4321
        '''

        if command not in self.scripts:
            print("That command does not exist")
            return

        script = self.scripts[command]
        if script['options'] is None:
            self.scripts[command]['function']()
        else:
            self.scripts[command]['function'](
                **self.options_dict(script, options))

    def options_dict(self, script, options):
        '''
        Takes in Command line options, converts them
        to a dictionary of arguements that can be passed to
        the utility function as kwargs

            :param script - the utility script being rna by the user
            :param options - list of strings that the user typed in
                Examples:
                 - ["port=5000", host="local", config="dev"]
                 The function parses these strings into key value pairs (key=value)

            :returns - arguement dictionary
        '''
        arguements = {}
        for option in options:
            try:
                switch, value = option.split("=")
            except ValueError:
                print("\033[1;37;41m   Options must be given a value,",
                      "ignoring....  \033[0m")
            if switch in script['options']:
                arguements[switch] = value
        return arguements

    def script(self, function_name, options=None):
        '''Decorator function to register a script'''
        def decorator(function):
            self.register_script(function_name, function, options)

        return decorator

    def register_script(self, function_name, function, options):
        self.scripts[function_name] = {
            'function': function,
            'options': options,
        }

    def register(self, utility):
        '''
            Registers a utility to the CLI
        '''
        for name, value in utility.scripts.items():
            self.register_script(f"{utility.utility_name}:{name}",
                                 value['function'], value['options'])

    def helper(self):
        '''
        Helper function
        '''
        print("Usage: python3 manage.py [COMMAND] [ARGUEMENTS ...]\n")
        print("Possible Options: ")
        for script, value in self.scripts.items():
            helper = value['function'].__doc__.strip('\n')
            name = format(script)
            print(name)
            print(helper)


class Utility():
    '''
        CLI Helper class
        Wrapper to create a group of utility functions

        When a utility is registered with the CLI, each of
        the utility's commands are added to the CLI's commands,
        with the utility's name preprended to them
        Examlple:
            Utility db
            db:create
            db:drop
            db:createuser
    '''
    def __init__(self, utility_name):
        self.utility_name = utility_name
        self.scripts = {}

    def script(self, function_name, options=None):
        '''Decorator function to register a script'''
        def decorator(function):
            self.register_script(function_name, function, options)

        return decorator

    def register_script(self, function_name, function, options):
        self.scripts[function_name] = {
            'function': function,
            'options': options
        }