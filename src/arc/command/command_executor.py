from typing import Callable, Any, TypedDict, Generator, Literal, ValuesView

from arc.color import effects, fg
from arc.errors import CommandError, ExecutionError, NoOpError
from arc import utils


# pylint: disable=inherit-non-class
class Callbacks(TypedDict):
    before: set[Callable]
    after: set[Callable]
    around: set[Callable]


class CommandExecutor:
    def __init__(self, function: Callable):
        self.function = function
        self.callbacks: Callbacks = {
            "before": set(),
            "around": set(),
            "after": set(),
        }

        self.__gens: list[Generator] = []

    def values(self) -> ValuesView[set]:
        ...

    @utils.timer("Command Execution")
    def execute(self, arguments: dict[str, Any]):
        BAR = "\u2500" * 40
        value = None
        try:
            self.before_callbacks(arguments)
            self.start_around_callbacks(arguments)
            utils.logger.debug(BAR)
            value = self.function(**arguments)
        except NoOpError as e:
            print(
                f"{fg.RED}This namespace cannot be executed. "
                f"Check --help for possible subcommands{effects.CLEAR}"
            )
        except ExecutionError as e:
            print(e)
        finally:
            utils.logger.debug(BAR)
            self.end_around_callbacks(value)
            self.after_callbacks(value)

        return value

    def register_callbacks(self, **kwargs):
        for when, callbacks in kwargs.items():
            for callback in callbacks:
                self.register_callback(when, callback)

    def register_callback(
        self, when: Literal["before", "around", "after"], call,
    ):
        if when not in ("before", "after", "around"):
            raise CommandError(
                f"Callback `when` must be before, after, or around, cannot be {when}"
            )

        self.callbacks[when].add(call)

    def before_callbacks(self, arguments: dict[str, Any]):
        if len(self.callbacks["before"]) > 0:
            utils.logger.debug(
                "Executing %sbefore%s callbacks", fg.YELLOW, effects.CLEAR
            )
            for callback in self.callbacks["before"]:
                callback(arguments)

    def after_callbacks(self, value: Any):
        if len(self.callbacks["after"]) > 0:
            utils.logger.debug(
                "Executing %safter%s callbacks", fg.YELLOW, effects.CLEAR
            )
            for callback in self.callbacks["after"]:
                callback(value)

    def start_around_callbacks(self, arguments):
        if len(self.callbacks["around"]) > 0:
            utils.logger.debug(
                "Starting %saround%s callbacks", fg.YELLOW, effects.CLEAR
            )
            for callback in self.callbacks["around"]:
                gen = callback(arguments)
                next(gen)
                self.__gens.append(gen)

    def end_around_callbacks(self, value):
        if len(self.callbacks["around"]) > 0:
            utils.logger.debug(
                "Completing %saround%s callbacks", fg.YELLOW, effects.CLEAR,
            )
            for callback in self.__gens:
                try:
                    callback.send(value)
                except StopIteration:
                    ...
