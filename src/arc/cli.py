import sys
from typing import Dict

from arc.__script_container import ScriptContainer
import arc._utils as util
from arc.utility import Utility
from arc.parser import Tokenizer, Parser, ScriptNode, UtilNode


class CLI(ScriptContainer):
    def __init__(self, utilities: list = None, arcfile=".arc"):
        super().__init__(arcfile)
        self.utilities: Dict[str, Utility] = {}

        if utilities is not None:
            self.install_utilities(*utilities)

    def __repr__(self):
        string: str = "---ARC CLI---\n"
        string += "Scripts: \n"
        string += "\n\t".join(c for c in self.scripts)
        string += "\nUtilities: \n"
        string += "\n\t".join(repr(self.utilities[util]) for util in self.utilities)
        return string

    def __call__(self, command=None):
        """Arc CLI driver method

        Tokenizes and Parses the user input, then passes
        on the resulting NodeTree to the correct execution method

        :param command: if present, will be used as the command string
        for the CLI to parse, instead of reading input from argv
        """
        input_string = " ".join(sys.argv[1:])
        if command:
            input_string = command

        tokens = Tokenizer(input_string).tokenize()
        parsed = Parser(tokens).parse()
        # util.logger(parsed)

        if isinstance(parsed, UtilNode):
            self.__execute_utility(parsed)
        elif isinstance(parsed, ScriptNode):
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

        if util_node.name not in self.utilities:
            print("That command does not exist")
            sys.exit(1)

        self.utilities[util_name](util_node.script)

    # def __interactive_mode(self):
    #     """Interactive version of Arc

    #     If the script is called with -i flag, the
    #     Arc script is entered in interactive mode.
    #     This means that the user can execute a number
    #     of commands while the program is still running.

    #     quit will exit

    #     clear will clear screen
    #     """
    #     cont = True
    #     while cont:

    #         user_input = input(">>> ")
    #         try:
    #             if user_input in ("q", "quit", "exit"):
    #                 cont = False
    #             elif user_input in ("c", "clear", "cls"):
    #                 util.clear()
    #             elif user_input in ("?", "h"):
    #                 self.helper()
    #             elif user_input != "":
    #                 split = user_input.split(" ")
    #                 self.__execute_utility(split[0], split[1:])
    #         except Exception as e:
    #             print(e)

    def install_utilities(self, *utilities):
        """Installs a series of utilities to the CLI"""
        for utility in utilities:
            if isinstance(utility, Utility):
                self.utilities[utility.name] = utility
                util.logger(f"Registered '{utility.name}' utility", state="debug")
            else:
                print(
                    "Only instances of the 'Utility'", "class can be registerd to Arc"
                )
                sys.exit(1)

    def helper(self):
        """Helper List function
        Prints out the docstrings for the CLI's scripts
        """
        print(
            "Usage: python3 FILENAME [COMMAND] [ARGUEMENTS ...]\n\n",
            "Possible options:\n",
            "-i : Enter interactive mode\n",
            "Scripts: ",
        )

        if len(self.scripts) > 0:
            for script_name, script in self.scripts.items():
                print(f"\033[92m{script_name}\033[00m\n    {script.doc}\n")
        else:
            print("No scripts installed")

        if len(self.utilities) > 0:
            print("\nInstalled Utilities")
            for _, utility in self.utilities.items():
                utility.helper()
        else:
            print("No utilities installed")
