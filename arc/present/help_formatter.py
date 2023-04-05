from __future__ import annotations

import textwrap
import typing as t
from itertools import repeat

from arc import constants
from arc.color import colorize, fx
from arc.config import PresentConfig
from arc.present.ansi import Ansi
from arc.present.formatters import TextFormatter
from arc.present.joiner import Join
from arc.present.markdown import MarkdownParser

if t.TYPE_CHECKING:
    from arc.define.command import Command
    from arc.define.documentation import Documentation, ParamDoc


class HelpFormatter(TextFormatter):
    _longest_intro: int = 0

    def __init__(
        self,
        doc: Documentation,
        config: PresentConfig,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        super().__init__(*args, **kwargs)
        self.doc = doc
        self.command = self.doc.command
        self.config = config
        self.color = config.color
        self.parser = MarkdownParser()

    @property
    def argument_params(self) -> list[ParamDoc]:
        return [param for param in self.doc.params if param["kind"] == "argument"]

    @property
    def key_params(self) -> list[ParamDoc]:
        return [param for param in self.doc.params if param["kind"] != "argument"]

    def format_help(self) -> str:
        self.write_help()
        res = self.parser.parse(self.value)
        return res.fmt(self.config)

    def format_usage(self) -> str:
        self.write_usage()
        res = self.parser.parse(self.value)
        return res.fmt(self.config)

    def write_help(self) -> None:
        doc = self.doc
        self.write_usage()

        if doc.description:
            with self.section(f"# DESCRIPTION"):
                self.write(doc.description)

        args = self.get_params(self.argument_params)
        options = self.get_params(self.key_params)
        subcommands = self.get_subcommands(
            self.command, self.command.subcommands.values()
        )

        longest = max(map(Ansi.len, (v[0] for v in args + options + subcommands))) + 2

        if args:
            self.write_section("# ARGUMENTS", args, longest)
        if options:
            self.write_section("# OPTIONS", options, longest)
        if subcommands:
            self.write_section("# SUBCOMMANDS", subcommands, longest)

        self.write(doc.sections)

    def write_usage(self) -> None:
        command = self.command

        with self.section("# USAGE"):
            self.write("```\n")
            if command.is_root and command.subcommands:
                params_str = self.usage_params(self.key_params, self.argument_params)
                self.write_text(
                    Join.with_space(
                        [
                            colorize(command.root.name, self.color.accent),
                            params_str,
                        ]
                    )
                )

                if self.doc.command.subcommands:
                    self.write_paragraph()
                    self.write_text(
                        Join.with_space(
                            [
                                colorize(command.root.name, self.color.accent),
                                colorize("<subcommand>", fx.UNDERLINE),
                                "[ARGUMENTS ...]",
                            ],
                            remove_falsey=True,
                        )
                    )
            else:
                params_str = self.usage_params(self.key_params, self.argument_params)
                fullname = self.doc.fullname
                path = " ".join(fullname[0:-1]) if fullname else ""
                name = colorize(fullname[-1], fx.UNDERLINE) if fullname else ""

                if not command.is_namespace:
                    self.write_text(
                        Join.with_space(
                            [
                                colorize(command.root.name, self.color.accent),
                                path,
                                name,
                                params_str,
                            ],
                            remove_falsey=True,
                        )
                    )
                    if self.doc.command.subcommands:
                        self.write_paragraph()

                if self.doc.command.subcommands:
                    self.write_text(
                        Join.with_space(
                            [
                                colorize(command.root.name, self.color.accent),
                                path,
                                name,
                                colorize("<subcommand>", fx.UNDERLINE),
                                "[ARGUMENTS ...]",
                            ],
                            remove_falsey=True,
                        )
                    )
            self.write("\n```")

    def usage_params(
        self, key_params: list[ParamDoc], arg_params: list[ParamDoc]
    ) -> str:
        formatted = []
        for param in sorted(
            key_params,
            key=lambda p: not p["optional"],
        ):
            if param["kind"] != "argument":
                formatted.append(self.format_single_param(param))

        # TODO: get this working in the parser
        # if len(formatted) > 0 and len(arg_params) > 0:
        #     formatted.append("[--]")

        for param in arg_params:
            if param["kind"] == "argument":
                formatted.append(self.format_single_param(param))

        return Join.with_space(formatted, remove_falsey=True)

    def format_single_param(self, param: ParamDoc) -> str:
        fmt = ""
        kind = param["kind"]
        name = param["name"]
        optional = param["optional"]

        if kind == "argument":
            fmt = name

            nargs = param["nargs"]
            if isinstance(nargs, int) and nargs:
                if optional:
                    fmt = Join.with_space(repeat(f"[{fmt}]", nargs))
                else:
                    fmt = Join.with_space(repeat(fmt, nargs))
            elif nargs == "*":
                fmt += f" [{fmt}...]"
                if optional:
                    fmt = f"[{fmt}]"
            else:
                if optional:
                    fmt = f"[{fmt}]"

        else:
            if param["short_name"] is not None:
                fmt = f"-{param['short_name']}"
            else:
                fmt = f"--{name}"

            if kind == "option":
                fmt += f" {param['name'].upper()}"

            if optional:
                fmt = f"[{fmt}]"

        return fmt

    def get_params(self, params: t.Collection[ParamDoc]) -> list[tuple[str, str]]:
        data = []
        for param in params:
            name: str = ""
            if param["kind"] == "argument":
                name = colorize(param["name"], self.color.accent)
            else:
                name = colorize(f"--{param['name']}", self.color.accent)
                if param["short_name"]:
                    name += colorize(f" (-{param['short_name']})", self.color.subtle)

            desc = textwrap.dedent(param["description"] or "")
            if (
                param["default"] not in (None, constants.MISSING)
                and param["kind"] != "flag"
            ):
                if isinstance(param["default"], constants.COLLECTION_TYPES):
                    default = Join.with_comma(param["default"])
                else:
                    default = param["default"]

                if desc:
                    desc += " "

                desc += f"[[color.subtle]](default: {default})[[/color.subtle]]"

            data.append((name, desc))

        return data

    def get_subcommands(
        self, parent: Command, commands: t.Collection[Command]
    ) -> list[tuple[str, str]]:
        data = []
        for command in commands:
            name = colorize(command.name, self.color.accent)
            desc = command.doc.short_description or ""
            aliases = parent.subcommands.aliases_for(command.name)
            if aliases:
                name += colorize(f" ({Join.with_comma(aliases)})", self.color.subtle)

            data.append((name, desc))

        return data

    def write_section(
        self, section: str, data: list[tuple[str, str]], longest: int
    ) -> None:
        with self.section(section):
            self.write("```\n")
            for name, desc in data:
                diff = longest - Ansi.len(name)

                desc = self.parser.parse_inline(desc.strip("\n")).fmt(self.config)

                self.write(
                    self.wrap_text(
                        f"{name}{' ' * diff}{desc}",
                        width=self.width,
                        initial_indent=" " * self.current_indent,
                        subsequent_indent=(" " * self.current_indent) + (" " * longest),
                    )
                )
                self.write_paragraph()
            self.write("```\n")

        # Quick fix for added empty line from self.section()
        self._buffer.pop()
