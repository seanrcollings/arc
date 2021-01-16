from arc.__script_container import ScriptContainer
from arc.utils import logger
from arc.color import fg, effects


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

    def __init__(self, name, description=None, script_type=None):
        super().__init__(script_type=script_type)
        self.name = name
        self.description = description
        logger.debug("Utility %s created'", name)

    def __call__(self, script_node):
        self.execute(script_node)

    def __repr__(self):
        return f"<Utility : {self.name}>"

    def helper(self):
        """Helper function for utilities
        Prints out the docstrings for the utilty's scripts"""

        print(f"{effects.BOLD}\nUtility {fg.YELLOW}{self.name}{effects.CLEAR}")
        if self.description:
            print(self.description)

        if len(self.scripts) > 0:
            print()
            for script in self.scripts.values():
                script.helper()
                print()
        else:
            print("No scripts defined")
