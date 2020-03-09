from arc import CLI
from arc.config import Config
from arc._utils import logger


class Utility(CLI):
    ''' CLI subclass to create a group of related scripts

    If the CLI finds that the first section of a command
    is a installed utility, it will pass control over to the utility
    which calls its own execute method
    Examlple:
        Utility db
        db:create
        db:drop
        db:createuser
    '''
    def __init__(self, name):
        super().__init__()
        self.name = name
        logger(f"Utility '{name}' created'")

    def __repr__(self):
        return "Utility"

    def __call__(self, command, options):
        self._execute(command, options)

    def helper(self):
        '''Helper function for utilities
        Prints out the docstrings for the utilty's scripts
        '''
        print(f"\nUtility \033[93m{self.name}\033[00m")
        print(
            f"Execute this utility with",
            f"\033[93m{self.name}\033[00m\033[92m{Config.utility_seperator}subcommand\033[00m"
        )

        if len(self.scripts) > 0:
            for script_name, script in self.scripts.items():
                print(
                    f"\033[92m{Config.utility_seperator}{script_name}\033[00m")
                print(f"\t{script.doc}\n")
        else:
            print("No scripts defined")
