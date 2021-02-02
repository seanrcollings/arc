import sys
from typing import Dict, List, Tuple

from arc.__script_container import ScriptContainer
from arc import utils
from arc.utility import Utility
from arc.parser import Tokenizer, Parser, ScriptNode, UtilNode
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

    def __call__(self, *args: str, **kwargs):
        """Arc CLI driver method

		Tokenizes and Parses the user input, then passes
		on the resulting NodeTree to the correct execution method
		"""
        input_list = self.__get_input__list(args, kwargs)
        tokens = Tokenizer(input_list).tokenize()
        parsed = Parser(tokens).parse()
        utils.logger.debug(parsed)

        if isinstance(parsed, UtilNode):
            with utils.handle(ArcError):
                self.__execute_utility(parsed)
        elif isinstance(parsed, ScriptNode):
            with utils.handle(ArcError):
                self.execute(parsed)
        else:
            raise RuntimeError("You shouldn't be here. Please report this bug")

    def __execute_utility(self, util_node: UtilNode):
        """Checks if a utility exists with provided user params

		If one does exist, pass the command and user_input onto it's
		execute method. If one doesn't exist, pass command and user_input
		on to the global CLI execute method.

		:param util_node: The Node tree created by the parser
		"""

        util_name = util_node.name

        if util_name not in self.utilities:
            raise ArcError(f"The utility '{util_name}' is not recognized")

        self.utilities[util_name](util_node.script)

    @staticmethod
    def __get_input__list(args: Tuple[str, ...], kwargs: Dict[str, str]) -> List[str]:
        if len(args) > 0:
            input_list = list(args)
            # Could also move this out of the if statement
            # to provide a way to force a value on the cli
            for key, value in kwargs.items():
                input_list.append(key + config.options_seperator + value)

        else:
            input_list = sys.argv[1:]

        return input_list

    def install_utilities(self, *utilities):
        """Installs a series of utilities to the CLI"""
        for utility in utilities:
            if isinstance(utility, Utility):
                if utility.script_type is None:
                    utility.script_type = self.script_type
                self.utilities[utility.name] = utility
                utils.logger.debug(
                    "%sRegistered '%s' utility %s",
                    fg.YELLOW,
                    utility.name,
                    effects.CLEAR,
                )
            else:
                raise ArcError(
                    "Only instances of the 'Utility'" "class can be registerd to ARC",
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
                f"{fg.YELLOW.bright}<utility>{config.utility_seperator}"
                f"{fg.GREEN.bright}<subcommand>{effects.CLEAR}"
            )
            for utility in self.utilities.values():
                utility.helper()
