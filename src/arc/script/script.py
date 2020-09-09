import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Tuple
from contextlib import contextmanager

from arc.errors import ScriptError, ExecutionError
from arc.script.__option import Option, NO_DEFAULT
from arc.script.__flag import Flag
import arc._utils as util


class Script(ABC):
    def __init__(
        self, name: str, function: Callable,
    ):

        self.name = name
        self.function: Callable = function
        self.options, self.flags = self.build_args(self.function)
        self.validation_errors: List[str] = []

        self.doc = "No Docstring"
        if self.function.__doc__ is not None:
            self.doc = self.function.__doc__.strip("\n\t ").replace("\n", "\n\t")

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def __call__(self, script_node):
        """External interface to execute a script"""
        self.validate_input(script_node)
        self.match_input(script_node)
        if len(self.validation_errors) == 0:
            self.execute(script_node)
        else:
            raise ScriptError(
                "Pre-script validation checks failed: \n",
                "\n".join(self.validation_errors),
            )

    @abstractmethod
    def execute(self, script_node):
        """Execution entry point of each script"""

    @abstractmethod
    def match_input(self, script_node):
        """Matches the input provided by script_node
        with the script's options and flags
        """

    @abstractmethod
    def build_args(self, function) -> Tuple[Dict[str, Option], Dict[str, Flag]]:
        """Builds the options and flag collections based
        on the function definition"""

    # HELPERS

    @staticmethod
    @contextmanager
    def catch():
        """Context Manager to catch and handle errors
        when calling the script's function"""
        try:
            util.logger("---------------------------")
            yield
        except ExecutionError as e:
            print(e)
            sys.exit(1)
        finally:
            util.logger("---------------------------")

    def assert_options_filled(self):
        for option in self.options.values():
            if option.value is NO_DEFAULT:
                raise ScriptError(f"No valued for required option '{option.name}'")

    def validate_input(self, script_node):
        """Helper function to check if user input is valid,
        should be overridden by child class

        If it isn't valid, add a reason to self.validation_errors
        """
        return True
