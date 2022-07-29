from __future__ import annotations
from itertools import repeat

import typing as t
import textwrap
from arc import constants

from arc.color import colorize, fg, effects
from arc.config import config
from arc.present.helpers import Joiner
from arc.utils import ansi_len
from arc.present.formatters import TextFormatter

if t.TYPE_CHECKING:
    from arc._command.documentation import Documentation, ParamDoc
    from arc._command.command import Command


def paragraphize(string: str) -> list[str]:
    return [textwrap.dedent(para).strip("\n") for para in string.split("\n\n")]


class HelpFormatter(TextFormatter):
    _longest_intro: int = 0

    def __init__(self, doc: Documentation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc = doc
        self.command = self.doc.command

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
            with self.section(config.default_section_name.upper()):
                self.write_text(paragraphize(doc.description))

        args = self.get_params(self.argument_params)
        options = self.get_params(self.key_params)
        subcommands = self.get_subcommands(
            self.command, self.command.subcommands.values()
        )

        longest = max(map(ansi_len, (v[0] for v in args + options + subcommands))) + 2

        if args:
            self.write_section("ARGUMENTS", args, longest)
        if options:
            self.write_section("OPTIONS", options, longest)
        if subcommands:
            self.write_section("SUBCOMMANDS", subcommands, longest)

        for section, body in doc.docstring.items():
            if section in {"arguments", config.default_section_name}:
                continue

            with self.section(section):
                self.write_text(paragraphize(body))

    def write_heading(self, heading: str):
        super().write_heading(colorize(heading.upper(), effects.BOLD))

    def write_usage(self):
        command = self.command

        with self.section("USAGE"):
            if command.is_root and command.subcommands:
                params_str = self.usage_params(
                    [p for p in self.key_params if p["name"] in command.SPECIAL_PARAMS],
                    self.argument_params,
                )
                global_param_str = self.usage_params(self.doc.global_params, [])
                self.write_text(
                    Joiner.with_space(
                        [colorize(command.root.name, config.brand_color), params_str]
                    )
                )

                if self.doc.command.subcommands:
                    self.write_paragraph()
                    self.write_text(
                        Joiner.with_space(
                            [
                                colorize(command.root.name, config.brand_color),
                                global_param_str,
                                colorize("<subcommand>", effects.UNDERLINE),
                                "[ARGUMENTS ...]",
                            ],
                            remove_falsey=True,
                        )
                    )
            else:
                params_str = self.usage_params(self.key_params, self.argument_params)
                fullname = self.doc.fullname
                path = " ".join(fullname[0:-1]) if fullname else ""
                name = colorize(fullname[-1], effects.UNDERLINE) if fullname else ""

                if not command.is_namespace:
                    self.write_text(
                        Joiner.with_space(
                            [
                                colorize(command.root.name, config.brand_color),
                                path,
                                name,
                                params_str,
                            ],
                            remove_falsey=True,
                        )
                    )

                if self.doc.command.subcommands:
                    self.write_paragraph()
                    self.write_text(
                        Joiner.with_space(
                            [
                                colorize(command.root.name, config.brand_color),
                                path,
                                name,
                                colorize("<subcommand>", effects.UNDERLINE),
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

        return Joiner.with_space(formatted, remove_falsey=True)

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
                    fmt = Joiner.with_space(repeat(f"[{fmt}]", nargs))
                else:
                    fmt = Joiner.with_space(repeat(fmt, nargs))
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
                name = colorize(param["name"], config.brand_color)
            else:
                name = colorize(f"--{param['name']}", config.brand_color)
                if param["short_name"]:
                    name += colorize(f" (-{param['short_name']})", fg.GREY)

            desc = textwrap.dedent(param["description"] or "")
            if (
                param["default"] not in (None, constants.MISSING)
                and param["kind"] != "flag"
            ):
                if isinstance(param["default"], constants.COLLECTION_TYPES):
                    default = Joiner.with_comma(param["default"])
                else:
                    default = param["default"]

                desc += colorize(f" (default: {default})", fg.GREY)

            desc = desc.strip("\n")

            data.append((name, desc))

        return data

    def get_subcommands(self, parent: Command, commands: t.Collection[Command]):
        data = []
        for command in commands:
            name = colorize(command.name, config.brand_color)
            desc = command.doc.short_description or ""
            aliases = parent.subcommands.aliases_for(command.name)
            if aliases:
                name += colorize(f" ({Joiner.with_comma(aliases)})", fg.GREY)

            data.append((name, desc))

        return data

    def write_section(self, section: str, data: list[tuple[str, str]], longest: int):
        with self.section(section):
            for name, desc in data:
                diff = longest - ansi_len(name)

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
