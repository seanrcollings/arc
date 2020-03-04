import sys
import time

from arc.config import Config
from arc.script import Script
from arc.errors import ExecutionError
from arc._utils import logger, clear


class CLI:
    def __init__(self, utilities: list = None, context_manager=None):
        self.scripts = {}
        self.context_manager = context_manager
        self._install_script(function=self.helper, name="help")

        # using type because isinstance tests for subclasses
        if type(self) is CLI:
            self.utilities = {}
            if utilities is not None:
                self.install_utilities(*utilities)

    def __call__(self):
        if len(sys.argv) < 2:
            print("You didn't provide any options.",
                  "Check 'help' for more information")
            return

        if "-i" in sys.argv:
            logger("Entering interactive mode")
            self.__interactive_mode()
            logger("Exiting interactive mode")
            return

        self.__execute_utility(sys.argv[1], sys.argv[2:])

    def __execute_utility(self, command, user_arguements):
        '''Checks if a utility exists with provided user params

        If one does exist, pass the command and user_arguements onto it's
        execute method. If one doesn't exist, pass command and user_arguements
        on to the global CLI execute method.

        :param command: the command that the user typed in i.e: run
        :param user_arguements: various user_arguements that the user passed in i.e: port=4321
        '''
        utility, command = self.__parse_command(command)

        if utility is not None:
            if utility not in self.utilities:
                print("That command does not exist")
                return

            self.utilities[utility](command, user_arguements)
        else:
            self._execute(command, user_arguements)

    def _execute(self, command: str, user_arguements: list):
        '''Executes the script from the user's command

        Execution time is recorded and logged at the end of the method.
        Excepts ExecutionErrors and prints their information

        :param command: the command that the user typed in i.e: run
        :param user_arguements: various user_arguements that the user passed in i.e: port=4321
        '''
        if command not in self.scripts:
            print("That command does not exist")
            return

        start_time = time.time()
        script = self.scripts[command]
        try:
            script.execute(context_manager=self.context_manager,
                           user_arguements=user_arguements)
        except ExecutionError as e:
            print(e)
            sys.exit(1)
        finally:
            end_time = time.time()
            logger(f"Completed in {end_time - start_time:.2f}s")

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

            if user_input in ("q", "quit", "exit"):
                cont = False
            elif user_input in ("c", "clear", "cls"):
                clear()
            elif user_input != "":
                split = user_input.split(" ")
                self.__execute_utility(split[0], split[1:])

    def script(self,
               name: str,
               options: list = None,
               named_arguements: bool = True):
        '''Decorator method used to register a script

        :param name: Name to register the script under, used on the command lin
        to run the script
        :param options: available command lines options for the script
        :param named_arguements: Specifies whether or not options require keywords
            True: All arguements require names, arguement that doesn't match
            the script's options will throw an exception
            False: Arguements do not require names, all arguements will be
            passed to the script (*args)
        '''
        def decorator(function):
            self._install_script(function, name, options, named_arguements)

        return decorator

    def _install_script(self,
                        function,
                        name,
                        options=None,
                        named_arguements=True):
        self.scripts[name] = Script(name, function, options, named_arguements)

    def install_utilities(self, *utilities):
        '''Installs a series of utilities to the CLI'''
        for utility in utilities:
            if repr(utility) == "Utility":  # work around for circular import
                self.utilities[utility.name] = utility
            else:
                print("Only instances of the 'Utility'",
                      "class can be registerd to Arc")
                sys.exit(1)

    def __parse_command(self, command: str):
        sep = Config.utility_seperator
        if sep in command:
            utility, command = command.split(sep)
        else:
            utility = None

        return utility, command

    def helper(self):
        '''Helper List function
        Prints out the docstrings for the clis's scripts
        '''
        print("Usage: python3 FILENAME [COMMAND] [ARGUEMENTS ...]\n")

        print("Possible Options: ")
        if len(self.scripts) > 0:
            for script_name, script in self.scripts.items():
                print(f"\033[92m{script_name}\033[00m\n    {script.doc}\n")
        else:
            print("No scripts installed")

        if len(self.utilities) > 0:
            print("\nInstalled Utilities")
            for _, utility in self.utilities.items():
                utility.helper()
