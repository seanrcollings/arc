from arc import CLI


class Utility(CLI):
    '''
    CLI Helper class
    Wrapper to create a group of utility functions

    If the CLI finds that the first section of a command
    is a installed utility, it will pass control over to the utility
    which then checks if the command is in it's scripts, then calls
    execute
    Examlple:
        Utility db
        db:create
        db:drop
        db:createuser
    '''
    def __init__(self, name, context_manager=None):
        super().__init__(context_manager=context_manager)
        self.name = name

    def __repr__(self):
        return "Utility"

    def __call__(self, command, options):
        self._execute(command, options)

    def helper(self):
        '''
        Helper function for utilities
        Prints out the docstrings for the utilty's scripts
        '''
        print(f"\nUtility \033[93m{self.name}\033[00m")
        print(f"Execute this utility with",
              "\033[93m{self.name}\033[00m\033[92m:subcommand\033[00m")

        if len(self.scripts) > 0:
            for script, value in self.scripts.items():
                helper_text = "No Docstring"
                doc = value['function'].__doc__
                if doc is not None:
                    helper_text = doc.strip('\n\t ')

                print(f"\033[92m:{script}\033[00m\n    {helper_text}\n")
        else:
            print("No scripts defined")
