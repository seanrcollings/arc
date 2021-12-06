from __future__ import annotations

import typing as t
from arc import logging
from arc.color import colored, colorize, fg, effects
from arc.config import config
from arc.execution_state import ExecutionState
from arc.command.param import Param
from arc.command.command import Command
from arc.utils import ansi_len
from arc.present.formatters import TextFormatter

logger = logging.getArcLogger("cdoc")


def print_help(command: Command, state: ExecutionState = None):
    f = HelpFormatter(width=80)
    f.write_help(command, state)
    print(f.value)


class HelpFormatter(TextFormatter):
    _longest_intro: int = 0

    def write_help(self, command: Command, state: ExecutionState = None):
        if not state:
            state = ExecutionState.empty()
            state.command_namespace = [command.name]  # type: ignore
            state.command_chain = [command]  # type: ignore

        state = t.cast(ExecutionState, state)

        self.write_usage(command, state)

        if command.description:
            with self.section("DESCRIPTION"):
                self.write_text(command.description)

        command.update_param_descriptions()

        self.write_params(command.executable.visible_params.values())

        for section, body in command.parsed_docstring.items():
            if section in {"arguments", "description"}:
                continue

            with self.section(section):
                self.write_text(body.split("\n\n"))

        self.write_subcommands(command.subcommands.values())

    def write_heading(self, heading: str):
        super().write_heading(colorize(heading.upper(), effects.BOLD))

    def write_usage(self, command: Command, state: ExecutionState):
        if command.is_namespace():
            command_str = f"{command.name}{config.namespace_sep}<subcommand>"
            params_str = "[arguments ...]"
        elif command is state.root:
            command_str = "<command>"
            params_str = "[arguments ...]"
        else:
            command_str = config.namespace_sep.join(state.command_namespace)
            params_str = self._param_str(command)

        with self.section("USAGE"):
            self.write_text(
                colored(
                    f"{colorize(state.root.name, fg.ARC_BLUE)} "
                    f"{colorize(command_str, effects.UNDERLINE)} {params_str}",
                )
            )

    def _param_str(self, command: Command):
        params = []
        for param in (
            param
            for param in command.executable.visible_params.values()
            if not param.is_positional
        ):
            params.append(format(param, "usage"))

        if len(params) > 0:
            params.append("[" + config.flag_prefix + "]")

        for param in command.executable.pos_params.values():
            params.append(format(param, "usage"))

        return " ".join(params)

    def write_params(self, params: t.Collection[Param]):
        data = [(format(param, "arguments"), param.description) for param in params]
        if not data:
            return

        # The length of the longest argument name
        longest = ansi_len(max(data, key=lambda v: ansi_len(v[0]))[0]) + 2
        self._longest_intro = longest

        with self.section("ARGUMENTS"):
            for name, desc in data:
                self.write(
                    self.wrap_text(
                        f"{name:<{longest}}{desc or ''}",
                        width=self.width,
                        initial_indent=" " * self.current_indent,
                        subsequent_indent=(" " * self.current_indent) + (" " * longest),
                    )
                )
                self.write_paragraph()

    def write_subcommands(self, commands: t.Collection[Command]):
        data = [
            (colored(colorize(command.name, fg.ARC_BLUE)), command.short_description)
            for command in commands
        ]

        if not data:
            return

        longest = ansi_len(max(data, key=lambda v: ansi_len(v[0]))[0]) + 2
        longest = max(self._longest_intro, longest)

        with self.section("SUBCOMMANDs"):
            for name, desc in data:
                self.write(
                    self.wrap_text(
                        f"{name:<{longest}}{desc or ''}",
                        width=self.width,
                        initial_indent=" " * self.current_indent,
                        subsequent_indent=(" " * self.current_indent) + (" " * longest),
                    )
                )
                self.write_paragraph()
