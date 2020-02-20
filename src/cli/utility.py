from cli import CLI


class Utility(CLI):
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
    def __init__(self, name, context_manager=None):
        self.name = name
        self.scripts = {}

        self.scripts["help"] = {
            "function": self.helper,
            "options": None,
            "named_arguements": True
        }

        self.context_manager = context_manager

    def __repr__(self):
        return "Utility"

    def __call__(self, command, options):
        self.execute(command, options)

    def helper(self):
        '''
        Helper function for utilities
        Prints out the docstrings for the utilty's scripts
        '''
        print(f"\nUtility \033[93m{self.name}\033[00m")
        print(f"Execute this utility with \033[93m{self.name}\033[00m\033[92m:subcommand\033[00m")
        if len(self.scripts) > 0:
            for script, value in self.scripts.items():
                helper_text = "No Docstring"
                if ( doc := value['function'].__doc__) is not None:
                    helper_text = doc.strip('\n\t ')

                print(f"\033[92m:{script}\033[00m\n    {helper_text}\n")
        else:
            print("No scripts defined")