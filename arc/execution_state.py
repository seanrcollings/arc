from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass
from arc.config import config

if TYPE_CHECKING:
    from arc.command.argument_parser import Parsed
    from arc.command import Command
    from arc.command.executable import Executable


@dataclass
class ExecutionState:
    """Central place to store state about the current command execution"""

    user_input: list[str]
    command_namespace: list[str]
    command_args: list[str]
    command_chain: list[Command]
    executable: Optional[Executable] = None
    parsed: Optional[Parsed] = None

    @property
    def root(self):
        return self.command_chain[0]

    @property
    def command(self):
        return self.command_chain[-1]

    @property
    def command_name(self):
        return config.namespace_sep.join(self.command_namespace)

    @classmethod
    def empty(cls):
        return ExecutionState(
            user_input=[],
            command_namespace=[],
            command_args=[],
            command_chain=[],
        )
