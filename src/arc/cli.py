import sys
import time
import logging

from arc.config import Config
from arc.script import Script
from arc.errors import ExecutionError


class CLI:
    config = Config

    def __init__(self, utilities: list = None, context_manager=None):
        self.scripts = {}
        self.context_manager = context_manager
        self._install_script(function=self.helper, name="help")

        if isinstance(self, CLI):
            # Sets up root logger Used to log information
            # to the console that can easily
            # suppressed for testing
            logging.basicConfig(level=self.config.logger_level)
            self.logger = logging.getLogger("cli")

            self.utilities = {}
            if utilities is not None:
                self.install_utilities(*utilities)

    def __call__(self):
        if len(sys.argv) < 2:
            print("You didn't provide any options.",
                  "Check 'help' for more information")
            return

        utility, command = self.__parse_command(sys.argv[1])
        options = sys.argv[2:]

        if utility is not None:
            if utility not in self.utilities:
                print("That command does not exist")
                return

            self.utilities[utility](command, options)
        else:
            self._execute(command, options)

    def _execute(self, command: str, options: list):
        '''Executes the script from the user's command

        If self.context_mangaer is not None, the command will be called
        within the context of said context manager, and will pass the managed resource
        as the first arguement to the script

        :param command: the command that the user typed in i.e: run
        :param options: various options that the user passed in i.e: port=4321
        '''
        if command not in self.scripts:
            print("That command does not exist")
            return

        start_time = time.time()
        script = self.scripts[command]
        try:
            script.execute(context_manager=self.context_manager,
                           user_arguements=options)
        except ExecutionError as e:
            print(e)
            sys.exit(1)
        finally:
            end_time = time.time()
            self.logger.info("Completed in %.2fs", end_time - start_time)

    def script(self,
               name: str,
               options: list = None,
               named_arguements: bool = True):
        '''Decorator method used to registering a script
        :param name: Name to register the script under, used on the command lin
        to run the script
        :param options: available command lines options for the script
        :param named_arguements: Specifies whether or not options require keywords
            True: All arguements require names, arguement that doesn't match
            the script's options will be ignored
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

    @staticmethod
    def __parse_command(command: str):
        if ":" in command:
            utility, command = command.split(":")
        else:
            utility = None

        return utility, command

    def helper(self):
        '''
        Helper List function
        Prints out the docstrings for the clis's scripts
        '''
        print("Usage: python3 FILENAME [COMMAND] [ARGUEMENTS ...]\n")

        print("Possible Options: ")
        if len(self.scripts) > 0:
            for script_name, script in self.scripts.items():
                print(f"\033[92m{script_name}\033[00m\n    {script.doc}\n")
        else:
            print("No scripts defined")

        if len(self.utilities) > 0:
            print("\nInstalled Utilities")
            for _, utility in self.utilities.items():
                utility.helper()
