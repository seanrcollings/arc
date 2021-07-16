from typing import Callable, Any, Generator, Literal
import pprint
import logging

from arc.color import fg, colorize
from arc.config import config
from arc import errors, utils
from arc.result import Ok, Err, Result

logger = logging.getLogger("arc_logger")
BAR = "\u2500" * 40


class CommandExecutor:
    """Handles the execution of a commands's function"""

    def __init__(self, function: Callable[..., Result]):
        self.function: Callable[..., Result] = function
        self.callbacks: dict[str, set[Callable]] = {
            "before": set(),
            "around": set(),
            "after": set(),
        }

        self.non_inheritable: set[Callable] = set()

        self.__gens: list[Generator] = []

    @utils.timer("Command Execution")
    def execute(self, _cli_namespace: list[str], arguments: dict[str, Any]):
        """Executes the command's functions

        Args:
            arguments (dict[str, Any]): Arguments parsed by an `ArgumentParser`

        Returns:
            Any: What the command's function returns
        """
        result: Result[Any, Any] = Ok()
        self.setup(arguments)

        try:
            logger.debug(BAR)
            result = self.call_function(arguments)
        finally:
            logger.debug(BAR)
            self.end_around_callbacks(result)
            self.after_callbacks(result)

        return result

    def setup(self, arguments: dict[str, Any]):
        self.before_callbacks(arguments)
        self.start_around_callbacks(arguments)
        logger.debug("Function Arguments: %s", pprint.pformat(arguments))

    def call_function(self, arguments):
        # The parsers always spit out a dictionary of arguements
        # and values. This doesn't allow *args to work, because you can't
        # spread *args after **kwargs. So the parser stores the *args in
        # _args and then we spread it manually. Note that this relies
        # on dictionaires being ordered
        if "_args" in arguments:
            var_args = arguments.pop("_args")
            result = self.function(*arguments.values(), *var_args)
        else:
            result = self.function(**arguments)

        if not isinstance(result, (Ok, Err)):
            return Ok(result)
        return result

    def inheritable_callbacks(self):
        return {
            key: {
                callback
                for callback in callbacks
                if callback not in self.non_inheritable
            }
            for key, callbacks in self.callbacks.items()
        }

    def register_callbacks(self, **kwargs):
        for when, callbacks in kwargs.items():
            for callback in callbacks:
                self.register_callback(when, callback)

    def register_callback(
        self, when: Literal["before", "around", "after"], call, inherit: bool = True
    ):
        if when not in self.callbacks.keys():
            raise errors.CommandError(
                f"Callback `when` must be before, after, or around, cannot be {when}"
            )

        self.callbacks[when].add(call)
        if not inherit:
            self.non_inheritable.add(call)

    def before_callbacks(self, arguments: dict[str, Any]):
        if len(self.callbacks["before"]) > 0:
            logger.debug("Executing %s callbacks", colorize("before", fg.YELLOW))
            for callback in self.callbacks["before"]:
                callback(arguments)

    def after_callbacks(self, value: Any):
        if len(self.callbacks["after"]) > 0:
            logger.debug("Executing %s callbacks", colorize("after", fg.YELLOW))
            for callback in self.callbacks["after"]:
                callback(value)

    def start_around_callbacks(self, arguments):
        if len(self.callbacks["around"]) > 0:
            logger.debug("Starting %s callbacks", colorize("around", fg.YELLOW))
            for callback in self.callbacks["around"]:
                gen = callback(arguments)
                next(gen)
                self.__gens.append(gen)

    def end_around_callbacks(self, value):
        if len(self.callbacks["around"]) > 0:
            logger.debug("Completing %s callbacks", colorize("around", fg.YELLOW))
            for callback in self.__gens:
                try:
                    callback.send(value)
                except StopIteration:
                    ...
