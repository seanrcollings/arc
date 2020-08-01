from abc import ABC, abstractmethod
import arc._utils as util
from arc.script import Script
from arc.config import Config
from arc.errors import ExecutionError


class ScriptContainer(ABC):
    '''Parent class of CLI and Utility'''
    def __init__(self, arcfile=None):
        self.scripts = {}

        if arcfile is not None and not Config._loaded:
            Config.load_arc_file(arcfile)

    @abstractmethod
    def __call__(self):
        pass

    def script(self,
               name: str,
               options: list = None,
               flags: list = None,
               pass_args: bool = False,
               pass_kwargs: bool = False):
        '''Installs a script to the container
        Creates a script object, appends it to
        the script container

        :param name: name of the script to be used on the comamnd line
        :param options: options available when running the script
        :param flags: flags (boolean values) available when running the script
        :param pass_args: specifies that the script passes all it's arguements
            positionally with *args
        :param pass_kwargs: specifies that this script passes all it's arguements
            with as key value pairs with **kwargs

        :returns: the provided function, for decorator chaining
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
