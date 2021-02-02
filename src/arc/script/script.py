import re
import sys
from abc import abstractmethod
from typing import Any, Callable, Dict, List, Tuple

from arc import config, utils
from arc.color import effects, fg
from arc.errors import ExecutionError, ScriptError, ValidationError
from arc.parser.data_types import ScriptNode

from .__flag import Flag
from .__option import Option
from .script_mixin import ScriptMixin


class Script(utils.Helpful, ScriptMixin):
    """Abstract Script Class, all Script types must inherit from it
    Helpful is abstract, so this is as well"""

    def __init__(self, name: str, function: Callable, meta: Any = None):

        self.name = name
        self.function: Callable = function
        self.options, self.flags = self.build_args()
        self.validation_errors: List[str] = []
        self.meta = meta

        self.doc = None
        if self.function.__doc__ is not None:
            doc = re.sub(r"\n\s+", "\n", self.function.__doc__)
            doc = re.sub(r"\n\t+", "\n", doc)
            self.doc = doc

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
            try:
                utils.logger.debug("---------------------------")
                self.execute(script_node)
            except ExecutionError as e:
                print(e)
            finally:
                utils.logger.debug("---------------------------")
        else:
            raise ScriptError(
                "Pre-script validation checks failed: \n",
                "\n".join(self.validation_errors),
            )

        self.cleanup()

    def build_args(self) -> Tuple[Dict[str, Option], Dict[str, Flag]]:
        """Builds the options and flag collections based
        on the function definition
        """
        with self.ArgBuilder(self.function) as builder:
            for idx, param in enumerate(builder):
                meta = builder.get_meta(index=idx)
                self.arg_hook(param, meta)

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

    def arg_hook(self, param, meta) -> None:
        """`build_args` hook.
        Can be used to check each of the args it's creating"""

    def validate_input(self, script_node) -> None:
        """Helper function to check if user input is valid,
        should be overridden by child class

        If it isn't valid, raise a `ValidationError`"""

    def cleanup(self):
        for _, option in self.options.items():
            option.cleanup()

    def helper(self):
        spaces = "  "
        print(
            utils.indent(
                f"{config.utility_seperator}{fg.GREEN}{self.name}{effects.CLEAR}",
                spaces,
            )
        )
        if self.doc:
            print(utils.indent(self.doc, spaces * 3))
        else:
            obj: utils.Helpful
            print(f"{spaces}Arguments:")
            for obj in [*self.options.values(), *self.flags.values()]:
                print(spaces * 3, end="")
                obj.helper()
