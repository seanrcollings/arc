from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Any
from dataclasses import dataclass


if TYPE_CHECKING:
    from arc.command import Command


@dataclass
class ExecutionState:
    """Central place to store state about the current command execution"""

    user_input: list[str]
    command_namespace: list[str]
    command_args: list[str]
    command_chain: list[Command]
    __ctx: Optional[dict[str, Any]] = None

    @property
    def root(self):
        return self.command_chain[0]

    @property
    def command(self):
        return self.command_chain[-1]

    @property
    def context(self):
        if self.__ctx is None:
            ctx: dict = {}
            for command in self.command_chain:
                ctx = command.context | ctx
            ctx["execution_state"] = self
            self.__ctx = ctx

        return self.__ctx

    @classmethod
    def empty(cls):
        return ExecutionState(
            user_input=[],
            command_namespace=[],
            command_args=[],
            command_chain=[],
        )
