import textwrap
from typing import Union
from arc.command import Command
from arc.color import fg, effects
from arc.config import config
from arc.run import find_command

__all__ = ["display_help", "generate_help"]


def header(text: str):
    return f"{effects.BOLD}{fg.WHITE.bright}{text.upper()}{effects.CLEAR}"


def section(heading: str, content: Union[str, list[str]]):
    if isinstance(content, list):
        content = textwrap.dedent("\n".join(content)).strip("\n")

    return header(heading) + "\n" + textwrap.indent(content, prefix="  ") + "\n\n"


class CommandDoc:

    DEFAULT_SECTION = "description"

    def __init__(self, doc: str = None, section_order: tuple = None):
        self.sections: dict[str, str] = {}
        self.order: tuple = section_order or tuple()
        if doc:
            self.parse_docstring(doc)

    def __str__(self):
        string = ""
        for key in self.order:
            string += section(key, self.sections[key].strip("\n"))

        for title, content in [
            (key, val) for key, val in self.sections.items() if key not in self.order
        ]:
            string += section(title, content.strip("\n"))

        return string.strip("\n")

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


def display_help(root: Command, command: Command, namespace: list[str]):
    print(generate_help(root, command, namespace))


def generate_help(root: Command, command: Command, namespace: list[str]) -> str:
    command_doc = CommandDoc()
    generate_usage(command_doc, root, command, namespace)
    command_doc.parse_docstring(command.doc or "")
    generate_aliases(command_doc, root, command, namespace)
    generate_subcommands(command_doc, command)
    return str(command_doc)


def generate_usage(
    doc: CommandDoc,
    root: Command,
    command: Command,
    namespace: list[str],
):
    if root == command:
        command_str = "<command>"
        args_str = "[arguments ...]"
    else:
        command_str = config.namespace_sep.join(namespace)
        args = []
        for arg in command.parser.args.values():
            if arg.is_flag():
                args.append(f"[{config.flag_denoter}{arg.name}]")
            else:
                arg_str = f"{arg.name}{config.arg_assignment}<...>"
                if arg.is_optional():
                    arg_str = f"[{arg_str}]"
                args.append(arg_str)

        args_str = " ".join(args)

    doc.add_section(
        "usage",
        f"{fg.ARC_BLUE}{root.name}{effects.CLEAR}"
        f" {effects.UNDERLINE}{command_str}{effects.CLEAR} {args_str}",
    )


def generate_aliases(
    doc: CommandDoc,
    root: Command,
    command: Command,
    namespace: list[str],
):
    parent, _ = find_command(root, namespace[:-1])
    aliases = [
        key for key, value in parent.subcommand_aliases.items() if value == command.name
    ]
    if aliases:
        aliases.append(command.name)
        doc.add_section("names", "\n".join(aliases))


def generate_subcommands(doc: CommandDoc, command: Command):
    if not command.subcommands:
        return

    name_size = len(max(command.subcommands.keys(), key=len))
    subcommands = ""

    for sub in command.subcommands.values():
        lines = CommandDoc(sub.doc).sections.get("description", "").split("\n")
        if len(lines) > 0:
            first_line = lines[0].strip("\n")
        else:
            first_line = ""
        subcommands += (
            f"{fg.ARC_BLUE}{sub.name:<{name_size}}{effects.CLEAR}   {first_line}\n"
        )

    doc.add_section("subcommands", subcommands)
