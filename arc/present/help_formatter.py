from __future__ import annotations

import textwrap
import typing as t
from itertools import repeat

from arc import constants
from arc.color import colorize, fx
from arc.config import ColorConfig
from arc.present.ansi import Ansi
from arc.present.formatters import TextFormatter
from arc.present.joiner import Join

if t.TYPE_CHECKING:
    from arc.define.command import Command
    from arc.define.documentation import Documentation, ParamDoc


def paragraphize(string: str) -> list[str]:
    return [textwrap.dedent(para).strip("\n") for para in string.split("\n\n")]


class HelpFormatter(TextFormatter):
    _longest_intro: int = 0

    def __init__(
        self,
        doc: Documentation,
        default_section_name: str,
        color: ColorConfig,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.doc = doc
        self.command = self.doc.command
        self.default_section_name = default_section_name
        self.color = color

    @property
    def argument_params(self):
        return [param for param in self.doc.params if param["kind"] == "argument"]

    @property
    def key_params(self):
        return [param for param in self.doc.params if param["kind"] != "argument"]

    def write_help(self):
        doc = self.doc
        self.write_usage()

        if doc.description:
            with self.section(self.default_section_name.upper()):
                self.write_text(paragraphize(doc.description))

        args = self.get_params(self.argument_params)
        options = self.get_params(self.key_params)
        subcommands = self.get_subcommands(
            self.command, self.command.subcommands.values()
        )

        longest = max(map(Ansi.len, (v[0] for v in args + options + subcommands))) + 2

        if args:
            self.write_section("ARGUMENTS", args, longest)
        if options:
            self.write_section("OPTIONS", options, longest)
        if subcommands:
            self.write_section("SUBCOMMANDS", subcommands, longest)

        for section, body in doc.docstring.items():
            if section in {"arguments", self.default_section_name}:
                continue

            with self.section(section):
                self.write_text(paragraphize(body))

    def write_heading(self, heading: str):
        super().write_heading(colorize(heading.upper(), fx.BOLD))

    def write_usage(self):
        command = self.command

        with self.section("USAGE"):
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

    def usage_params(self, key_params: list[ParamDoc], arg_params: list[ParamDoc]):
        formatted = []
        for param in sorted(
            key_params,
            key=lambda p: not p["optional"],
        ):
            if param["kind"] != "argument":
                formatted.append(self.format_single_param(param))

        if len(formatted) > 0 and len(arg_params) > 0:
            formatted.append("[--]")

        for param in arg_params:
            if param["kind"] == "argument":
                formatted.append(self.format_single_param(param))

        return Join.with_space(formatted, remove_falsey=True)

    def format_single_param(self, param: ParamDoc):
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

    def get_params(self, params: t.Collection[ParamDoc]):
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

                desc += colorize(f" (default: {default})", self.color.subtle)

            desc = desc.strip("\n")

            data.append((name, desc))

        return data

    def get_subcommands(self, parent: Command, commands: t.Collection[Command]):
        data = []
        for command in commands:
            name = colorize(command.name, self.color.accent)
            desc = command.doc.short_description or ""
            aliases = parent.subcommands.aliases_for(command.name)
            if aliases:
                name += colorize(f" ({Join.with_comma(aliases)})", self.color.subtle)

            data.append((name, desc))

        return data

    def write_section(self, section: str, data: list[tuple[str, str]], longest: int):
        with self.section(section):
            for name, desc in data:
                diff = longest - Ansi.len(name)

                self.write(
                    self.wrap_text(
                        f"{name}{' ' * diff}{desc}",
                        width=self.width,
                        initial_indent=" " * self.current_indent,
                        subsequent_indent=(" " * self.current_indent) + (" " * longest),
                    )
                )
                self.write_paragraph()

        # Quick fix for added empty line from self.section()
        self._buffer.pop()
