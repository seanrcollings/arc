import sys
from typing import Dict, List, Union

from arc.__script_container import ScriptContainer
from arc import utils
from arc.utility import Utility
from arc.parser import parse, CommandNode
from arc import config
from arc.errors import ArcError
from arc.color import fg, effects


class CLI(ScriptContainer, utils.Helpful):
    def __init__(self, *args, utilities: list = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.utilities: Dict[str, Utility] = {}

        if utilities is not None:
            self.install_utilities(*utilities)

    def __repr__(self):
        string: str = "---ARC CLI---\n"
        string += "Scripts: \n"
        string += "\n".join(c for c in self.scripts)
        string += "\nUtilities: \n"
        string += "\n\t".join(repr(self.utilities[util]) for util in self.utilities)

        return string

    def __call__(self, execute: Union[List[str], str, None] = None):
        """Arc CLI driver method

		Tokenizes and Parses the user input, then passes
		on the resulting NodeTree to the correct execution method

        Checks if a utility exists with provided user params
		If one does exist, pass the command and user_input onto it's
		execute method. If one doesn't exist, pass command and user_input
		on to the global CLI execute method.
		"""
        input_list = execute if execute else sys.argv[1:]
        command_node = parse(input_list)
        utils.logger.debug(command_node)

        command_name = command_node.namespace[0]

        if command_name in self.utilities:
            self.__execute_utility(command_node)
        elif command_name in self.scripts:
            self.execute(command_node)
        else:
            print(f"No utility or script with name '{command_name}' registered")
            sys.exit(1)

    def __execute_utility(self, command_node: CommandNode):
        """Executes a utility
		:param util_node: The Node tree created by the parser
		"""

        command_name = command_node.namespace.pop(0)
        self.utilities[command_name](command_node)

    def install_utilities(self, *utilities):
        """Installs a series of utilities to the CLI"""
        for utility in utilities:
            if isinstance(utility, Utility):
                if utility.script_type is None:
                    utility.script_type = self.script_type
                self.utilities[utility.name] = utility
                utils.logger.debug("Registered '%s' utility", utility.name)
            else:
                raise ArcError(
                    "Only instances of the 'Utility'", "class can be registerd to ARC",
                )

    def helper(self):
        """Helper List function
		Prints out the docstrings for the CLI's scripts
		"""
        print(f"Usage: python3 {sys.argv[0]} [COMMAND] [ARGUMENTS ...]\n\n",)

        header = effects.BOLD + effects.UNDERLINE + "{title}" + effects.CLEAR + ":\n"

        print(header.format(title="Installed Scripts"))
        if len(self.scripts) > 0:
            for _, script in self.scripts.items():
                script.helper()
        else:
            print("No Scripts Installed")

        if len(self.utilities) > 0:
            print(f"\n{header.format(title='Installed Utilities')}")
            print(
                "Execute a utility with: "
                f"{fg.YELLOW.bright}<utility>"
                f"{fg.GREEN.bright}{config.utility_seperator}<subcommand>{effects.CLEAR}"
            )
            for utility in self.utilities.values():
                utility.helper()
