import textwrap
import re
from typing import Union, Optional
from arc.command import Command
from arc.color import fg, effects
from arc import config
from arc.run import find_command


def display_help(root: Command, command: Command, namespace: list[str]):
    help_text = (
        ""
        + generate_usage(root, command, namespace)
        + generate_sections(command.doc)
        + generate_aliases(root, command, namespace)
        + generate_subcommands(command)
    ).strip("\n")

    print(help_text)


def generate_usage(root: Command, command: Command, namespace: list[str]) -> str:
    if root == command:
        command_str = "<command>"
        arg_str = "[arguments ...]"
    else:
        command_str = config.namespace_sep.join(namespace)
        arg_str = " ".join(arg.helper() for arg in command.parser.args.values())

    return section(
        "usage",
        f"{fg.ARC_BLUE}{root.name}{effects.CLEAR}"
        f" {effects.UNDERLINE}{command_str}{effects.CLEAR} {arg_str}",
    )


def generate_sections(doc: Optional[str]):
    formatted = ""
    if doc:
        command_doc = CommandDoc(doc)
        for heading, content in command_doc.sections.items():
            formatted += section(heading, content)

    return formatted


def generate_aliases(root: Command, command: Command, namespace: list[str]):
    parent, _ = find_command(root, namespace[:-1])
    aliases = [
        key for key, value in parent.subcommand_aliases.items() if value == command.name
    ]
    if aliases:
        return section("aliases", aliases)
    return ""


def generate_subcommands(command: Command):
    if not command.subcommands:
        return ""

    name_size = len(max(command.subcommands.keys(), key=len))
    subcommands = ""

    for sub in command.subcommands.values():
        lines = CommandDoc(sub.doc).description.split("\n")
        if len(lines) > 0:
            first_line = lines[0].strip("\n")
        else:
            first_line = ""
        subcommands += (
            f"{fg.ARC_BLUE}{sub.name:<{name_size}}{effects.CLEAR}   {first_line}\n"
        )

    return section("subcommands", subcommands)


class CommandDoc:
    def __init__(self, doc: str = None):
        self.doc: Optional[str] = doc
        self.sections: dict[str, str] = {}

        if doc:
            lines = doc.split("\n")
            self.doc = "\n".join(line.strip() for line in lines)

            match = re.match(
                r"(\A(?!#).+?(?:#|\Z))", self.doc, re.DOTALL | re.MULTILINE
            )
            if match:
                self.sections["description"] = match.group().rstrip("#\n")

            sections = self.doc.split("\n#")
            if self.sections.get("description"):
                sections = sections[1:]

            for section in sections:
                lines = section.split("\n")
                self.sections[lines[0].strip()] = textwrap.dedent(
                    "\n".join(lines[1:]).strip("\n")
                )

    @property
    def description(self):
        return self.sections.get("description", "")


def header(text: str):
    return f"{effects.BOLD}{fg.WHITE.bright}{text.upper()}{effects.CLEAR}"


def section(heading: str, content: Union[str, list[str]]):
    if isinstance(content, list):
        content = textwrap.dedent("\n".join(content)).strip("\n")

    return header(heading) + "\n" + textwrap.indent(content, prefix="  ") + "\n\n"
