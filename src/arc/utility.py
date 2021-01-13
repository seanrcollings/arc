from arc.__script_container import ScriptContainer
from arc._utils import logger
from arc import config


class Utility(ScriptContainer):
    """CLI subclass to create a group of related scripts

    If the CLI finds that the first section of a command
    is a installed utility, it will pass control over to the utility
    which calls its own execute method
    Examlple:
        Utility db
        db:create
        db:drop
        db:createuser
    """

    def __init__(self, name, *args, script_type=None, **kwargs):
        super().__init__(*args, script_type=script_type, **kwargs)  # type: ignore
        self.name = name
        logger.debug("Utility %s created'", name)

    def __call__(self, script_node):
        self.execute(script_node)

    def __repr__(self):
        return f"<Utility : {self.name}>"

    def helper(self):
        """Helper function for utilities
        Prints out the docstrings for the utilty's scripts
        """
        print(f"\nUtility \033[93m{self.name}\033[00m")
        print(
            "Execute this utility with"
            f"\033[93m{self.name}\033[00m\033[92m{config.utility_seperator}subcommand\033[00m",
        )

        if len(self.scripts) > 0:
            for script_name, script in self.scripts.items():
                print(f"\033[92m{config.utility_seperator}{script_name}\033[00m")
                print(f"\t{script.doc}\n")
        else:
            print("No scripts defined")
