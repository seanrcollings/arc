from typing import Optional
from dataclasses import dataclass
from arc.command import Command, Context


@dataclass
class ExecutionState:
    user_input: list[str]
    command_namespace: list[str]
    command_args: list[str]
    command_chain: list[Command]
    command: Command
    _ctx: Optional[Context] = None

    @property
    def context(self):
        if self._ctx is None:
            ctx: dict = {}
            for command in self.command_chain:
                ctx = command.context | ctx
            ctx["execution_state"] = self
            self._ctx = Context(ctx)

        return self._ctx
