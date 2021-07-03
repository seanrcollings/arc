from typing import Callable, Any, Generator, Literal
import pprint
import logging

from arc.color import effects, fg
from arc import errors
from arc import utils


logger = logging.getLogger("arc_logger")


class CommandExecutor:
    """Handles the execution of a commands's function"""

    def __init__(self, function: Callable):
        self.function: Callable = function
        self.callbacks: dict[str, set[Callable]] = {
            "before": set(),
            "around": set(),
            "after": set(),
        }

        self.non_inheritable: set[Callable] = set()

        self.__gens: list[Generator] = []

    @utils.timer("Command Execution")
    def execute(self, arguments: dict[str, Any]):
        """Executes the command's functions

        Args:
            arguments (dict[str, Any]): Arguments parsed by an `ArgumentParser`

        Returns:
            Any: What the command's function returns
        """
        BAR = "\u2500" * 40
        value = None
        try:
            self.before_callbacks(arguments)
            self.start_around_callbacks(arguments)
            logger.debug("Function Arguments: %s", pprint.pformat(arguments))
            logger.debug(BAR)
            # The parsers always spit out a dictionary of arguements
            # and values. This doesn't allow *args to work, because you can't
            # spread *args after **kwargs. So the parser stores the *args in
            # _args and then we spread it manually. Note that this relies
            # on dictionaires being ordered
            if "_args" in arguments:
                var_args = arguments.pop("_args")
                value = self.function(*arguments.values(), *var_args)
            else:
                value = self.function(**arguments)

        except errors.NoOpError as e:
            print(
                f"{fg.RED}This namespace cannot be executed. "
                f"Check --help for possible subcommands{effects.CLEAR}"
            )
        except errors.ExecutionError as e:
            logger.error(e)
        finally:
            logger.debug(BAR)
            self.end_around_callbacks(value)
            self.after_callbacks(value)

        return value

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

    @utils.handle(errors.ValidationError)
    def before_callbacks(self, arguments: dict[str, Any]):
        if len(self.callbacks["before"]) > 0:
            logger.debug("Executing %sbefore%s callbacks", fg.YELLOW, effects.CLEAR)
            for callback in self.callbacks["before"]:
                callback(arguments)

    @utils.handle(errors.ValidationError)
    def after_callbacks(self, value: Any):
        if len(self.callbacks["after"]) > 0:
            logger.debug("Executing %safter%s callbacks", fg.YELLOW, effects.CLEAR)
            for callback in self.callbacks["after"]:
                callback(value)

    @utils.handle(errors.ValidationError)
    def start_around_callbacks(self, arguments):
        if len(self.callbacks["around"]) > 0:
            logger.debug("Starting %saround%s callbacks", fg.YELLOW, effects.CLEAR)
            for callback in self.callbacks["around"]:
                gen = callback(arguments)
                next(gen)
                self.__gens.append(gen)

    @utils.handle(errors.ValidationError)
    def end_around_callbacks(self, value):
        if len(self.callbacks["around"]) > 0:
            logger.debug(
                "Completing %saround%s callbacks",
                fg.YELLOW,
                effects.CLEAR,
            )
            for callback in self.__gens:
                try:
                    callback.send(value)
                except StopIteration:
                    ...
