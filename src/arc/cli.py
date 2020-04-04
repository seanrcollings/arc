import sys

from arc.__script_container import ScriptContainer
from arc.config import Config
import arc._utils as util
from arc.utility import Utility

VERSION = "0.8.1"


class CLI(ScriptContainer):
    def __init__(self, utilities: list = None, arcfile=".arc"):
        super().__init__(arcfile=arcfile)
        self.script("help")(self.helper)
        self.utilities = {}
        if utilities is not None:
            self.install_utilities(*utilities)

    def __call__(self):
        '''Arc CLI driver method

        Runs rudimentary checks agains sys.argv.
        This is the ONLY place sys.argv should be accessed
        all other methods that need the info from sys.argv
        will be passed it from this method
        '''
        if len(sys.argv) < 2:
            if Config.anon_identifier in self.scripts:
                self.execute(Config.anon_identifier, [])
            else:
                print("You didn't provide any options.",
                      "Check 'help' for more information")

        elif "-i" in sys.argv:
            util.logger("Entering interactive mode", state="ok")
            self.__interactive_mode()
            util.logger("Exiting interactive mode", state="ok")
            return

        elif "--version" in sys.argv or "-v" in sys.argv:
            print(VERSION)
            return

        else:
            self.__execute_utility(sys.argv[1], sys.argv[2:])

    def __execute_utility(self, command: str, user_input: list):
        '''Checks if a utility exists with provided user params

        If one does exist, pass the command and user_input onto it's
        execute method. If one doesn't exist, pass command and user_input
        on to the global CLI execute method.

        :param command: the command that the user typed in i.e: run
        :param user_input: various user_input that the user passed in i.e: port=4321
        '''
        utility, command = self.__parse_command(command)

        if utility is not None:
            if utility not in self.utilities:
                print("That command does not exist")
                return

            self.utilities[utility](command, user_input)
        else:
            self.execute(command, user_input)

    def __interactive_mode(self):
        '''Interactive version of Arc

        If the script is called with -i flag, the
        Arc script is entered in interactive mode.
        This means that the user can execute a number
        of commands while the program is still running.

        quit will exit

        clear will clear screen
        '''
        cont = True
        while cont:

            user_input = input(">>> ")
            try:
                if user_input in ("q", "quit", "exit"):
                    cont = False
                elif user_input in ("c", "clear", "cls"):
                    util.clear()
                elif user_input in ("?", "h"):
                    self.helper()
                elif user_input != "":
                    split = user_input.split(" ")
                    self.__execute_utility(split[0], split[1:])
            except Exception as e:
                print(e)

    def install_utilities(self, *utilities):
        '''Installs a series of utilities to the CLI'''
        for utility in utilities:
            if isinstance(utility, Utility):  # work around for circular import
                self.utilities[utility.name] = utility
                util.logger(f"Registered '{utility.name}' utility",
                            state="debug")
            else:
                print("Only instances of the 'Utility'",
                      "class can be registerd to Arc")
                sys.exit(1)

    @staticmethod
    def __parse_command(command: str) -> tuple:
        '''Parses a provided user command, checks if utility'''
        sep = Config.utility_seperator
        if sep in command:
            utility, command = command.split(sep)
        else:
            utility = None

        return (utility, command)

    def helper(self):
        '''Helper List function
        Prints out the docstrings for the CLI's scripts
        '''
        print("Usage: python3 FILENAME [COMMAND] [ARGUEMENTS ...]\n")
        print("Possible options:")
        print("-i : Enter interactive mode")
        print()
        print("Scripts: ")
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
