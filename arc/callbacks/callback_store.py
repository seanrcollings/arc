from __future__ import annotations
from typing import Any, Callable, Generator
import logging

from arc.color import fg, colorize

from arc import errors
from arc.result import Result
from arc.callbacks.callbacks import CallbackTime

logger = logging.getLogger("arc_logger")


class CallbackStore:
    """Stores and handles the execution of callback functions"""

    def __init__(self):
        self.callbacks: dict[CallbackTime, set[Callable]] = {
            "before": set(),
            "around": set(),
            "after": set(),
        }

        self.non_inheritable: set[Callable] = set()

        self.__gens: list[Generator] = []

    def __getitem__(self, key: CallbackTime):
        return self.callbacks[key]

    def pre_execution(self, arguments: dict[str, Any]):
        self.exec_callbacks("before", arguments)
        self.start_around_callbacks(arguments)

    def post_execution(self, result: Result):
        self.end_around_callbacks(result)
        self.exec_callbacks("after", result)

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
        self, when: CallbackTime, call: Callable, inherit: bool = True
    ):
        if when not in self.callbacks.keys():
            raise errors.CommandError(
                f"Callback `when` must be before, after, or around, cannot be {when}"
            )

        self.callbacks[when].add(call)
        if not inherit:
            self.non_inheritable.add(call)

    def exec_callbacks(self, when: CallbackTime, *arguments):
        if len(self.callbacks[when]) > 0:
            logger.debug("Executing %s callbacks", colorize(when, fg.YELLOW))
            for callback in self.callbacks[when]:
                callback(*arguments)

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
