from __future__ import annotations
import re
import textwrap
from typing import Union

from arc import errors
from arc.color import colorize, fg, effects
from arc.config import config
from arc.execution_state import ExecutionState


class CommandDoc:

    DEFAULT_SECTION = config.default_section_name

    def __init__(self, doc: str, state: ExecutionState, section_order: tuple = None):
        self.docstring = doc
        self.state = state
        self.sections: dict[str, str] = {}
        self.order: tuple = section_order or tuple()

        self.parse_docstring(doc)
        self.generate_usage()
        self.generate_subcommands()
        self.generate_aliases()
        if config.parse_argument_help:
            self.parse_argument_section()

    def __str__(self):
        string = ""
        for key in self.order:
            string += self.section(key, self.sections[key].strip("\n"))

        for title, content in [
            (key, val) for key, val in self.sections.items() if key not in self.order
        ]:
            string += self.section(title, content.strip("\n"))

        return string.strip("\n")

    @property
    def description(self):
        return self.sections.get("description", "")

    @property
    def short_description(self):
        return self.description.split("\n")[0]

    ### Parsers ###
    def parse_docstring(self, doc: str):
        """Parses a doc string into sections

        Sections are denoted by a new line, and
        then a line beginning with `#`. Whatever
        comes after the `#` will be the key in
        the sections dict. And all content between
        that `#` and the next `#` will be the value.

        The first section of the docstring is not
        required to possess a section header, and
        will be entered in as the `description` section.
        """
        lines = [line.strip() for line in doc.split("\n")]
        current_section = self.DEFAULT_SECTION

        for line in lines:
            if line.startswith("#"):
                current_section = line[1:].strip()
            elif line != "" or current_section != self.DEFAULT_SECTION:
                self.update_section(current_section, line + "\n")

    # TODO: Cleanup this function, it's super clunky as is
    def parse_argument_section(self):
        arguments_str = self.sections.get("arguments")
        if not arguments_str:
            return

        arguments_str = arguments_str.strip("\n")
        arguments: list[list[str]] = list(
            list(string.strip("\n").strip(" ") for string in found)
            for found in re.findall(
                r"^(?P<name>[^:]+):(?P<desc>[^:]+)(?=\n+.+:|\Z)",
                arguments_str,
                re.DOTALL | re.MULTILINE,
            )
        )
        if not arguments:
            raise errors.ParserError(
                "Argument section Parsing failed. The argument section "
                f"of {self.state.command.name}'s documentation does not follow the "
                "expected format. \nReference "
                + colorize(
                    "https://github.com/seanrcollings/arc/wiki/Help-Documentation ",
                    fg.YELLOW,
                )
                + "for help with formatting or add "
                + colorize("parse_argument_help=False", fg.YELLOW)
                + "to your config"
            )

        # Format the names first so we can calculate the proper
        # alignment for all the descriptions
        for i, (name, _) in enumerate(arguments):
            argument = self.state.command.executable.params.get(name)
            if not argument:
                raise errors.ParserError(
                    f"Argument section Parsing failed. No arg named {name}"
                )

            formatted_name = format(argument)
            if argument.short:
                formatted_name += f" ({format(argument, 'short')})"
            arguments[i][0] = formatted_name

        name_max_len = len(max(arguments, key=lambda n: len(n[0]))[0])
        indent = name_max_len + 5

        formatted_str = ""
        for name, desc in arguments:
            lines = desc.split("\n", maxsplit=1)
            first = lines[0]
            rest = lines[1:]
            split_name = name.split(" ", 1)

            colored_name = colorize(split_name[0], fg.ARC_BLUE)
            if len(split_name) > 1:
                colored_name += " " + colorize("".join(split_name[1:]), fg.GREY)

            first_line_indent = " " * (name_max_len - len(name) + 5)
            formatted_str += f"{colored_name}{first_line_indent}{first}\n"
            if rest:
                formatted_str += textwrap.indent("\n".join(rest), " " * (indent)) + "\n"

        self.add_section("arguments", formatted_str)

    ### Generators ###

    def generate_usage(self):
        if self.state.command.is_namespace():
            command_str = f"{self.state.command.name}{config.namespace_sep}<subcommand>"
            args_str = "[arguments ...]"
        elif self.state.root == self.state.command:
            command_str = "<command>"
            args_str = "[arguments ...]"
        else:
            command_str = config.namespace_sep.join(self.state.command_namespace)
            args_str = self.generate_options_string()

        self.add_section(
            "usage",
            f"{fg.ARC_BLUE}{self.state.root.name}{effects.CLEAR}"
            f" {effects.UNDERLINE}{command_str}{effects.CLEAR} {args_str}",
        )

    def generate_options_string(self):
        args = []
        for arg in (
            arg
            for arg in self.state.command.executable.params.values()
            if not arg.hidden and not arg.is_positional
        ):
            string = format(arg, "usage")
            args.append(string)

        args.append("[" + config.flag_denoter + "]")

        for arg in self.state.command.executable.pos_params.values():
            args.append(format(arg))

        return " ".join(args)

    def generate_subcommands(self):
        if not self.state.command.subcommands:
            return

        name_size = len(max(self.state.command.subcommands.keys(), key=len))
        subcommands = ""

        for sub in self.state.command.subcommands.values():
            if sub.function.__doc__:
                short = sub.function.__doc__.split("\n")[0]
            else:
                short = ""

            subcommands += (
                f"{fg.ARC_BLUE}{sub.name:<{name_size}}" f"{effects.CLEAR}   {short}\n"
            )

        self.add_section("subcommands", subcommands)

    def generate_aliases(self):
        chain = self.state.command_chain

        if len(chain) <= 1:
            return

        parent = chain[-2]
        aliases = [
            key
            for key, value in parent.subcommand_aliases.items()
            if value == self.state.command.name
        ]
        if aliases:
            aliases.append(self.state.command.name)
            self.add_section("names", "\n".join(aliases))

    ### Helpers ###

    def add_section(self, title: str, content: str):
        """Adds a section with `title` and `content`"""
        self.sections[title] = content

    def update_section(self, key: str, to_add: str):
        """Updates a section. If that section
        does not exist, creates it"""
        key = key.lower().strip()
        if key in self.sections:
            self.sections[key] += to_add
        else:
            self.add_section(key, to_add)

    @staticmethod
    def header(text: str):
        return f"{effects.BOLD}{fg.WHITE.bright}{text.upper()}{effects.CLEAR}"

    @staticmethod
    def section(heading: str, content: Union[str, list[str]]):
        if isinstance(content, list):
            content = textwrap.dedent("\n".join(content)).strip("\n")

        return (
            CommandDoc.header(heading)
            + "\n"
            + textwrap.indent(content, prefix="  ")
            + "\n\n"
        )
