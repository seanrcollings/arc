"""Autcompletion support for the fish shell"""
from typing import Union
from pathlib import Path
from arc import types
from arc.config import config
from arc.command import Command, helpers
from arc.execution_state import ExecutionState

COMPLETE = "complete -c"
SEEN_SUBCOMMAND = "__fish_seen_subcommand_from"

# TODO: stip out use of ParsingMethod


class FishCompletion:
    def __init__(self, command: str):
        self.lines: list[str] = []
        self._buffer = ""
        self.command = command

    def __str__(self):
        self.flush()
        return "\n".join(self.lines)

    def add(self, content: str, no_format=False):
        if no_format:
            self.lines.append(content)
        else:
            self.lines.append(f"{COMPLETE} {self.command}{content}")

    def comment(self, comment: str):
        self.add(f"\n# {comment}", no_format=True)
        return self

    def flush(self):
        if self._buffer:
            self.add(self._buffer)
            self._buffer = ""

        return self

    def _buffer_add(self, content: str):
        self._buffer += " " + content
        return self

    def set(self, name: str, value: str):
        self.lines.append(f"set -l {name} {value}")
        return self

    def no_files(self):
        return self._buffer_add("-f")

    def force_files(self):
        return self._buffer_add("-F")

    def description(self, desc: str):
        return self._buffer_add(f'-d "{desc}"')

    def arguments(self, args: Union[list[str], str]):
        if isinstance(args, list):
            args = " ".join(args)

        return self._buffer_add(f'-a "{args}"')

    def long(self, name: str):
        return self._buffer_add(f"-l {name}")

    def short(self, name: str):
        return self._buffer_add(f"-s {name}")

    def keep_order(self):
        return self._buffer_add("-k")

    def required(self):
        return self._buffer_add("-r")

    def exclusive(self):
        return self._buffer_add("-x")

    def condition(self, condition: str):
        return self._buffer_add(f'-n "{condition}"')

    def seen_subcommand(self, *args: str):
        return self.condition(f"{SEEN_SUBCOMMAND} {' '.join(args)}")

    def not_seen_subcommand(self, *args: str):
        return self.condition(f"not {SEEN_SUBCOMMAND} {' '.join(args)}")


def generate(name: str, root: Command) -> str:
    commands = [
        command for command in helpers.get_all_commands(root) if command[0] != root
    ]

    completions = (
        FishCompletion(name)
        .comment("Setup")
        .set("commands", " ".join(name for _, name in commands))
        .no_files()
        .flush()
    )

    completions.comment("Help").seen_subcommand("help").arguments("$commands").flush()

    completions.comment("Commands")
    command_completions(completions, commands)
    for command, cmd_name in commands:
        argument_completions(completions, command, cmd_name)

    return str(completions)


def command_completions(
    completions: FishCompletion, commands: list[tuple[Command, str]]
):

    for command, cmd_name in commands:
        state = ExecutionState.empty()
        state.command_chain = [command]
        (
            completions.not_seen_subcommand("$commands")
            .arguments(cmd_name)
            .description(command.doc(state).short_description)
            .flush()
        )


def argument_completions(completions: FishCompletion, command: Command, cmd_name: str):
    completions.comment(f"{cmd_name} Arguments")
    for arg in command.executable.params.values():

        if arg.hidden or arg.is_positional:
            continue

        else:
            completions.seen_subcommand(cmd_name).long(arg.arg_alias)
            if arg.short:
                completions.short(arg.short)

        completions.description(f"{types.type_store.get_display_name(arg.annotation)}")
        if types.safe_issubclass(arg.annotation, Path):
            completions.force_files()
        else:
            completions.no_files()

        completions.flush()
