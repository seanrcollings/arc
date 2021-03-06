from abc import ABC, abstractmethod
from typing import Dict

import arc.utils as util
from arc.script import script_factory
from arc.script.script import Script
from arc import config
from arc.errors import ScriptError
from arc.script import ScriptType


class ScriptContainer(ABC):
    """Parent class of CLI and Utility"""

    def __init__(self, arcfile="./.arc", script_type=ScriptType.KEYWORD):
        self.script_type = script_type
        self.scripts: Dict[str, Script] = {}
        self.script("help", script_type=ScriptType.KEYWORD)(self.helper)

        config.load_arc_file(arcfile)

    @abstractmethod
    def __call__(self):
        ...

    def script(self, name=None, script_type=None, **kwargs):
        """decorator wrapper around install_script"""

        def decorator(function):
            return self.install_script(name, function, script_type, **kwargs)

        return decorator

    def install_script(self, name, function, script_type=None, **kwargs):
        """Installs a script to the container
        Creates a script object, appends it to
        the script container

        :returns: the provided function, for decorator chaining. As such,
            you can give one function multiple script names
        """
        # Fallback for script type:
        #   - provided arguement
        #   - script_type of the container (if it's a util it can also inherit
        #        it's type from it's parent)
        #   - Defaults to KEYWORD
        script_type = script_type or self.script_type or ScriptType.KEYWORD
        script = script_factory(name, function, script_type, **kwargs)
        self.scripts[script.name] = script

        util.logger.debug(
            "registered '%s' script to %s", script.name, self.__class__.__name__,
        )
        return function

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
        ...
