from abc import ABC, abstractmethod
from typing import Dict, Type
import arc._utils as util
from arc.script import script_factory
from arc.script.script import Script
from arc.config import Config
from arc.errors import ExecutionError, ScriptError


class ScriptContainer(ABC):
    """Parent class of CLI and Utility"""

    def __init__(self, arcdir=".", arcfile=".arc"):
        self.scripts: Dict[str, Type[Script]] = {}
        self.script("help")(self.helper)

        if arcfile is not None and not Config._loaded:
            Config.load_arc_file(f"{arcdir}/{arcfile}")

    @abstractmethod
    def __call__(self):
        pass

    def script(self, name=None, positional=False):
        """Installs a script to the container
        Creates a script object, appends it to
        the script container

        :returns: the provided function, for decorator chaining. As such,
            you can give one function multiple script names
        """

        def decorator(function):

            script = script_factory(name=name, positional=positional, function=function)
            self.scripts[script.name] = script
            util.logger(f"Registered '{script.name}' script", state="debug")
            return function

        return decorator

    @util.timer
    def execute(self, script_node):
        """Executes the script from the user's command

        :param script_node: ScriptNode object generated by the parser
            contains both the options and flags for the script

        :raises ScriptError: If the command doesn't exist

        :excepts ExecutionError: Raised during the execution of a script anytime
            bad data is passed or something unexpected happens
        """

        script_name = script_node.name
        if script_name not in self.scripts:
            raise ScriptError(f"The script '{script_name}' is not recognized")

        script = self.scripts[script_name]
        try:
            script(script_node)
        except ExecutionError as e:
            print(e)

    @abstractmethod
    def helper(self):
        pass
