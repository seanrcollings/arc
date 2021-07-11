"""Autcompletion support for the fish shell"""
from typing import Union
from pathlib import Path
from arc.config import config
from arc.command import Command, helpers, ParsingMethod

COMPLETE = "complete -c "
SEEN_SUBCOMMAND = "__fish_seen_subcommand_from"


class FishCompletion:
    def __init__(self, command: str):
        self.lines: list[str] = []
        self._buffer = ""
        self.command = command

    def __str__(self):
        self.flush()
        return "\n".join(self.lines)

    def add(self, content: str):
        self.lines.append(f"{COMPLETE}{self.command}{content}")

    def flush(self):
        if self._buffer:
            self.add(self._buffer)
            self._buffer = ""

        return self

    def _buffer_add(self, content: str):
        self._buffer += " " + content

    def set(self, name: str, value: str):
        self.lines.append(f"set -l {name} {value}")
        return self

    def no_files(self):
        self._buffer_add("-f")
        return self

    def force_files(self):
        self._buffer_add("-F")
        return self

    def description(self, desc: str):
        self._buffer_add(f'-d "{desc}"')
        return self

    def arguments(self, args: Union[list[str], str]):
        if isinstance(args, list):
            args = " ".join(args)

        self._buffer_add(f'-a "{args}"')
        return self

    def long(self, name: str):
        self._buffer_add(f"-l {name}")
        return self

    def short(self, name: str):
        self._buffer_add(f"-s {name}")
        return self

    def keep_order(self):
        self._buffer_add("-k")
        return self

    def required(self):
        self._buffer_add("-r")
        return self

    def exclusive(self):
        self._buffer_add("-x")
        return self

    def condition(self, condition: str):
        self._buffer_add(f'-n "{condition}"')
        return self

    def seen_subcommand(self, *args: str):
        return self.condition(f"{SEEN_SUBCOMMAND} {' '.join(args)}")

    def not_seen_subcommand(self, *args: str):
        return self.condition(f"not {SEEN_SUBCOMMAND} {' '.join(args)}")


def generate(name: str, root: Command):
    # comp = f"complete -c {name}"
    commands = helpers.get_all_commands(root)

    completions = (
        FishCompletion(name)
        .set("commands", " ".join(name for _, name in commands))
        .no_files()
        .flush()
    )

    for command, cmd_name in commands:
        if command == root:
            continue

        desc = command.doc.split("\n")[0]
        (
            completions.not_seen_subcommand("$commands")
            .arguments(cmd_name)
            .description(desc)
            .flush()
        )

    for command, cmd_name in commands:
        if command == root:
            continue

        for arg in command.parser.args.values():
            if arg.hidden:
                continue

            parse_type = type(command.parser)
            if arg.is_flag():
                (
                    completions.seen_subcommand(cmd_name)
                    .short(arg.name[0])
                    .long(arg.name)
                )

            elif parse_type is ParsingMethod.STANDARD:
                (completions.seen_subcommand(cmd_name).required().long(arg.name))
            elif parse_type is ParsingMethod.KEYWORD:
                completions.seen_subcommand(cmd_name).arguments(
                    f"{arg.name}{config.arg_assignment}"
                )

            if issubclass(arg.annotation, Path):
                completions.force_files()
            else:
                completions.no_files()

            completions.flush()

    print(completions)
