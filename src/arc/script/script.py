import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Tuple
from contextlib import contextmanager

from arc.errors import ScriptError, ExecutionError
from arc.parser.data_types import ScriptNode
from arc.script.__option import Option, NO_DEFAULT
from arc.script.__flag import Flag
import arc._utils as util
from .script_mixin import ScriptMixin


class Script(ABC, ScriptMixin):
    def __init__(
        self, name: str, function: Callable,
    ):

        self.name = name
        self.function: Callable = function
        self.options, self.flags = self.build_args()
        self.validation_errors: List[str] = []

        self.doc = "No Docstring"
        if self.function.__doc__ is not None:
            self.doc = self.function.__doc__.strip("\n\t ").replace("\n", "\n\t")

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def __call__(self, script_node):
        """External interface to execute a script

        Handles a few things behind the scenes
            - calls self.validate_input
            - calls self.match_input
        Both of these can be defined in the
        children classes, and will never need to be called
        directly by the child class

        :param script_node: SciptNode object created by the parser
            May contain options, flags and arbitrary args

        """
        self.validate_input(script_node)
        if len(self.validation_errors) == 0:
            self.match_input(script_node)
            self.execute(script_node)
        else:
            raise ScriptError(
                "Pre-script validation checks failed: \n",
                "\n".join(self.validation_errors),
            )

    def build_args(self) -> Tuple[Dict[str, Option], Dict[str, Flag]]:
        with self.ArgBuilder(self.function) as builder:

            for idx, param in enumerate(builder):
                builder.param = param
                builder.idx = idx
                self.arg_hook(builder)

            return builder.args

    @abstractmethod
    def execute(self, script_node: ScriptNode):
        """Execution entry point of each script

        :param script_node: SciptNode object created by the parser.
        None of the Script classes use script_node in their implementation
        of execute, but they may need to so it passes it currently
        """

    @abstractmethod
    def match_input(self, script_node: ScriptNode) -> None:
        """Matches the input provided by script_node
        with the script's options and flags. Should mutate
        state because this function returns None. For example,
        options values should be set on their respective option
        in self.options

        :param script_node: ScriptNode object created by the parser
        Has had the UtilNode stripped away if it existed
        """

    @abstractmethod
    def arg_hook(self, builder):
        """Builds the options and flag collections based
        on the function definition

        :param function: User-defined function that get's called by the script.
        """

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
