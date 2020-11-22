from abc import ABC, abstractmethod
from typing import Dict, Type
import arc._utils as util
from arc.script import script_factory
from arc.script.script import Script
from arc import config
from arc.errors import ScriptError
from arc.script import ScriptType


class ScriptContainer(ABC):
    """Parent class of CLI and Utility"""

    def __init__(self, arcfile=".arc", script_type=ScriptType.KEYWORD):
        self.script_type = script_type
        self.scripts: Dict[str, Type[Script]] = {}
        self.script("help", script_type=ScriptType.KEYWORD)(self.helper)

        config.load_arc_file(arcfile)

    @abstractmethod
    def __call__(self):
        pass

    def script(self, name=None, script_type=None, **kwargs):
        """Installs a script to the container
        Creates a script object, appends it to
        the script container

        :returns: the provided function, for decorator chaining. As such,
            you can give one function multiple script names
        """
        # Fallback for script type:
        #   - provided arguement
        #   - script_type of the container (if it's a util it can also inherit it's type)
        #   - Defaults to KEYWORD
        script_type = script_type or self.script_type or ScriptType.KEYWORD

        def decorator(function):
            script = script_factory(name, function, script_type, **kwargs)
            self.scripts[script.name] = script
            util.logger.debug(
                "registered '%s' script to %s", script.name, self.__class__.__name__,
            )
            return function

        return decorator

    def install_script(self, name, function, script_type=None, **kwargs):
        """Alias function for the decorator. Makes adding scripts programmatically easier"""
        return self.script(name, script_type, **kwargs)(function)

    @util.timer
    def execute(self, script_node):
        """Executes the script from the user's command

        :param script_node: ScriptNode object generated by the parser
            contains both the options and flags for the script

        :raises ScriptError: If the command doesn't exist

        """

        if script_node.name not in self.scripts:
            raise ScriptError(f"The script '{script_node.name}' is not recognized")

        script = self.scripts[script_node.name]
        script(script_node)

    @abstractmethod
    def helper(self):
        pass
