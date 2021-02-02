from abc import abstractmethod
from typing import List, Dict, Callable, Any
import re

from arc.errors import ScriptError, ValidationError
from arc.parser import CommandNode
from arc.utils import Helpful, indent, logger
from arc import config
from arc.color import fg, effects
from .__option import Option
from .script_mixin import ScriptMixin


class Script(Helpful, ScriptMixin):
    """Abstract Script Class, all Script types must inherit from it
    Helpful is abstract, so this is as well"""

    def __init__(self, name: str, function: Callable, meta: Any = None):

        self.name = name
        self.function: Callable = function
        self.args = self.build_args()
        self.validation_errors: List[str] = []
        self.meta = meta

        self.doc = None
        if self.function.__doc__ is not None:
            doc = re.sub(r"\n\s+", "\n", self.function.__doc__)
            doc = re.sub(r"\n\t+", "\n", doc)
            self.doc = doc

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self.name}>"

    def __call__(self, command_node):
        """External interface to execute a script

        Handles a few things behind the scenes
            - calls self.validate_input
            - calls self.match_input
        Both of these can be defined in the
        children classes, and will never need to be called
        directly by the child class

        :param command_node: SciptNode object created by the parser
            May contain options, flags and arbitrary args

        """
        try:
            self.validate_input(command_node)
        except ValidationError as e:
            self.validation_errors.append(str(e))

        if len(self.validation_errors) == 0:
            self.match_input(command_node)
            logger.debug(self.args)
            self.execute(command_node)
        else:
            raise ScriptError(
                "Pre-script validation checks failed: \n",
                "\n".join(self.validation_errors),
            )

        self.cleanup()

    def build_args(self) -> Dict[str, Option]:
        """Builds the options and flag collections based
        on the function definition
        """
        with self.ArgBuilder(self.function) as builder:
            for idx, param in enumerate(builder):
                meta = builder.get_meta(index=idx)
                self.arg_hook(param, meta)

            return builder.args

    @abstractmethod
    def execute(self, command_node: CommandNode):
        """Execution entry point of each script

        :param command_node: SciptNode object created by the parser.
        None of the Script classes use command_node in their implementation
        of execute, but they may need to so it passes it currently
        """

    @abstractmethod
    def match_input(self, command_node: CommandNode) -> None:
        """Matches the input provided by command_node
        with the script's options and flags. Should mutate
        state because this function returns None. For example,
        options values should be set on their respective option
        in self.options

        :param command_node: ScriptNode object created by the parser
        Has had the UtilNode stripped away if it existed
        """

    def arg_hook(self, param, meta) -> None:
        """`build_args` hook.
        Can be used to check each of the args it's creating"""

    def validate_input(self, command_node) -> None:
        """Helper function to check if user input is valid,
        should be overridden by child class

        If it isn't valid, raise a `ValidationError`"""

    def cleanup(self):
        for option in self.args.values():
            option.cleanup()

    def helper(self):
        spaces = "  "
        print(
            indent(
                f"{config.utility_seperator}{fg.GREEN}{self.name}{effects.CLEAR}",
                spaces,
            )
        )
        if self.doc:
            print(indent(self.doc, spaces * 3))
        else:
            obj: Helpful
            print(f"{spaces}Arguments:")
            for obj in self.args.values():
                print(spaces * 3, end="")
                obj.helper()
