from __future__ import annotations

import typing as t
import textwrap
from arc import logging
from arc.color import colored, colorize, fg, effects
from arc.config import config
from arc.context import Context
from arc.command.param import Param
from arc.utils import ansi_len
from arc.present.formatters import TextFormatter

if t.TYPE_CHECKING:
    from arc.command.command import Command


logger = logging.getArcLogger("cdoc")


def paragraphize(string: str) -> list[str]:
    return [textwrap.dedent(para).strip("\n") for para in string.split("\n\n")]


class HelpFormatter(TextFormatter):
    _longest_intro: int = 0

    def write_help(self, command: Command, ctx: Context):
        self.write_usage(command, ctx)

        if command.description:
            with self.section("DESCRIPTION"):
                self.write_text(paragraphize(command.description))

        command.update_param_descriptions()

        self.write_params(command.visible_params)

        for section, body in command.parsed_docstring.items():
            if section in {"arguments", "description"}:
                continue

            with self.section(section):
                self.write_text(paragraphize(body))

        self.write_subcommands(command, command.subcommands.values())

    def write_heading(self, heading: str):
        super().write_heading(colorize(heading.upper(), effects.BOLD))

    # TODO: usage doesn't properly take standalone commands
    # vs CLI into consideration
    def write_usage(self, command: Command, ctx: Context):
        if command.is_namespace():
            command_str = f"{command.name}{config.namespace_sep}<subcommand>"
            params_str = "[arguments ...]"
        elif command is ctx.root.command:
            command_str = "<command>"
            params_str = "[arguments ...]"
        else:
            command_str = ctx.fullname
            params_str = self._param_str(command)

        with self.section("USAGE"):
            self.write_text(
                colored(
                    f"{colorize(ctx.root.command.name, config.brand_color)} "
                    f"{colorize(command_str, effects.UNDERLINE)} {params_str}",
                )
            )

    def _param_str(self, command: Command):
        params = []
        for param in (
            param for param in command.visible_params if not param.is_positional
        ):
            params.append(format(param, "usage"))

        if len(params) > 0:
            params.append("[" + config.flag_prefix + "]")

        for param in command.pos_params:
            params.append(format(param, "usage"))

        return " ".join(params)

    def write_params(self, params: t.Collection[Param]):
        data = [
            (
                format(param, "arguments"),
                textwrap.dedent(param.description or "").strip("\n"),
            )
            for param in params
        ]
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

        # Quick fix for added empty line from self.section()
        self._buffer.pop()

    def write_subcommands(self, parent: Command, commands: t.Collection[Command]):
        data = []
        for command in commands:
            name = colored(colorize(command.name, config.brand_color))
            desc = command.short_description
            aliases = tuple(
                alias
                for alias, name in parent.subcommand_aliases.items()
                if name == command.name
            )
            if aliases:
                name = colored(
                    name + colorize(" (" + ", ".join(aliases) + ")", fg.GREY)
                )

            data.append((name, desc))

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

        self._buffer.pop()