from abc import ABC, abstractmethod
import arc._utils as util
from arc.script import Script
from arc.config import Config
from arc.errors import ExecutionError


class ScriptContainer(ABC):
    def __init__(self, arcfile=None):
        self.scripts = {}

        # loads values from the specified
        # arcfile and sets them on the config object
        if not Config._loaded and arcfile is not None:
            Config.load_arc_file(arcfile)
            util.logger("--- Arc file Loaded ---", state="debug")

    @abstractmethod
    def __call__(self):
        pass

    def script(self,
               name: str,
               options: list = None,
               flags: list = None,
               pass_args: bool = False,
               pass_kwargs: bool = False):
        '''Decorator method used to install a script
        Installs a script to the CLI or Utility
        Creates a script object, and adds it to the
        scripts dictionary with the script's name as it's key
        and the script object as it's value
        '''
        def decorator(function):
            script = Script(name, function, options, flags, pass_args,
                            pass_kwargs)

            self.scripts[name] = script
            util.logger(f"Registered '{name}' script", state="debug")
            return function

        return decorator

    @util.timer
    def execute(self, command: str, user_input: list):
        '''Executes the script from the user's command

        :param command: the command that the user typed in i.e: run
        :param user_input: various user_input that the user passed in i.e: port=4321

        :excepts ExecutionError: Raised during the execution of a script anytime
            bad data is passed or something unexpected happens
        '''

        if command not in self.scripts:
            if Config.anon_identifier in self.scripts:
                user_input.append(command)
                command = Config.anon_identifier
            else:
                print("That command does not exist")
                return

        script = self.scripts[command]
        try:
            script(user_input=user_input)
        except ExecutionError as e:
            print(e)
