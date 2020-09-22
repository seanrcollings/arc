from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Tuple

from arc.errors import ScriptError, ValidationError
from arc.parser.data_types import ScriptNode
from .__option import Option
from .__flag import Flag
from .script_mixin import ScriptMixin


class Script(ABC, ScriptMixin):
    def __init__(
        self,
        name: str,
        function: Callable,
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
        try:
            self.validate_input(script_node)
        except ValidationError as e:
            self.validation_errors.append(str(e))

        if len(self.validation_errors) == 0:
            self.match_input(script_node)
            self.execute(script_node)
        else:
            raise ScriptError(
                "Pre-script validation checks failed: \n",
                "\n".join(self.validation_errors),
            )

    def build_args(self) -> Tuple[Dict[str, Option], Dict[str, Flag]]:
        """Builds the options and flag collections based
        on the function definition
        """
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

    def arg_hook(self, builder):
        """build_args hook.
        Can be used to check each of the args it's creating"""

    def validate_input(self, script_node):
        """Helper function to check if user input is valid,
        should be overridden by child class

        If it isn't valid, raise a ValidationError"""
