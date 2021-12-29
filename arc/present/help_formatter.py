from __future__ import annotations

import typing as t
import textwrap
from arc import constants, logging
from arc.color import colored, colorize, fg, effects
from arc.config import config
from arc.context import Context
from arc._command.param import Param
from arc.utils import ansi_len
from arc.present.formatters import TextFormatter

if t.TYPE_CHECKING:
    from arc._command.command import Command


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

        self.write_params("ARGUMENTS", command.pos_params)
        self.write_params("OPTIONS", command.flag_params + command.key_params)

        for section, body in command.parsed_docstring.items():
            if section in {"arguments", "description"}:
                continue

            with self.section(section):
                self.write_text(paragraphize(body))

        self.write_subcommands(command, command.subcommands.values())

    def write_heading(self, heading: str):
        super().write_heading(colorize(heading.upper(), effects.BOLD))

    def write_usage(self, command: Command, ctx: Context):
        from arc.cli import CLI

        with self.section("USAGE"):
            if command.is_namespace():
                command_str = f"{command.name}{constants.NAMESPACE_SEP}<subcommand>"
                self.write_text(
                    colored(
                        f"{colorize(ctx.root.command.name, config.brand_color)} "
                        f"{colorize(command_str, effects.UNDERLINE)} [ARGUMENTS ...]",
                    )
                )
            elif isinstance(command, CLI):
                self.write_text(
                    colored(
                        f"{colorize(ctx.root.command.name, config.brand_color)} [OPTIONS] "
                        f"{colorize('<command>', effects.UNDERLINE)} [ARGUMENTS ...]",
                    )
                )
            else:
                command_str = ctx.fullname
                params_str = self._param_str(command)

                if ctx.command is ctx.root.command:
                    self.write_text(
                        colored(
                            f"{colorize(command_str, config.brand_color)} {params_str}"
                        )
                    )
                else:
                    self.write_text(
                        colored(
                            f"{colorize(ctx.root.command.name, config.brand_color)} "
                            f"{colorize(command_str, effects.UNDERLINE)} {params_str}"
                        )
                    )

    def _param_str(self, command: Command):
        params = []
        for param in sorted(
            command.key_params + command.flag_params,
            key=lambda p: not p.optional,
        ):
            params.append(format(param, "usage"))

        if len(params) > 0 and len(command.pos_params) > 0:
            params.append("[" + constants.FLAG_PREFIX + "]")

        for param in command.pos_params:
            params.append(format(param, "usage"))

        return " ".join(params)

    def write_params(self, section: str, params: t.Collection[Param]):
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

        with self.section(section):
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
