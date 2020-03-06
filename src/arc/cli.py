import sys
import time

from arc.config import Config
from arc.script import Script
from arc.errors import ExecutionError
from arc._utils import logger, clear


class CLI:
    def __init__(self, utilities: list = None, arcfile=".arc"):
        self.scripts = {}
        self._install_script(function=self.helper, name="help")
        self.before = None

        # using type because isinstance tests for subclasses
        if type(self) is CLI:
            self.utilities = {}
            if utilities is not None:
                self.install_utilities(*utilities)

        # loads values from the specified
        # arcfile and sets them on the config object
        Config.load_arc_file(arcfile)

    def __call__(self):
        '''Arc cli driver method

        Runs rudimentary checks agains sys.argv.
        This is the ONLY place sys.argv should be accessed
        all other methods that need the info from sys.argv
        will be passed it from this method
        '''
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

    def __execute_utility(self, command, user_input):
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
            self._execute(command, user_input)

    def _execute(self, command: str, user_input: list):
        '''Executes the script from the user's command

        Execution time is recorded and logged at the end of the method.
        Excepts ExecutionErrors and prints their information

        :param command: the command that the user typed in i.e: run
        :param user_input: various user_input that the user passed in i.e: port=4321
        '''
        if command not in self.scripts:
            print("That command does not exist")
            return

        start_time = time.time()
        script = self.scripts[command]
        try:
            script(user_input=user_input, before=self.before)
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
            elif user_input in ("?", "h"):
                self.helper()
            elif user_input != "":
                split = user_input.split(" ")
                self.__execute_utility(split[0], split[1:])

    def script(self,
               name: str,
               options: list = None,
               flags: list = None,
               pass_args: bool = False,
               pass_kwargs: bool = False):
        '''Decorator method used to register a script'''
        def decorator(function):
            self._install_script(function, name, options, flags, pass_args,
                                 pass_kwargs)

        return decorator

    # TODO: Reimplement context managers / work on before_actions
    # def before_action(self):
    #     def decorator(function):
    #         self.before = function

    #     return decorator

    def _install_script(self,
                        function,
                        name,
                        options=None,
                        flags=None,
                        pass_args=False,
                        pass_kwargs=False):
        self.scripts[name] = Script(name, function, options, flags, pass_args,
                                    pass_kwargs)

    def install_utilities(self, *utilities):
        '''Installs a series of utilities to the CLI'''
        for utility in utilities:
            if repr(utility) == "Utility":  # work around for circular import
                self.utilities[utility.name] = utility
            else:
                print("Only instances of the 'Utility'",
                      "class can be registerd to Arc")
                sys.exit(1)

    @staticmethod
    def __parse_command(command: str):
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
        else:
            print("No utilities installed")
