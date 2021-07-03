import textwrap
from typing import Union
from arc.command import Command
from arc.color import fg, effects
from arc import config


def header(text: str):
    return f"{effects.BOLD}{fg.WHITE.bright}{text.upper()}{effects.CLEAR}"


def section(heading: str, content: Union[str, list[str]]):
    if isinstance(content, list):
        content = textwrap.dedent("\n".join(content)).strip("\n")

    return header(heading) + "\n" + textwrap.indent(content, prefix="  ") + "\n\n"


def display_help(root: Command, command: Command, namespace: list[str]):
    help_text = ""

    if root == command:
        command_str = "<command>"
        arg_str = "[arguments ...]"
    else:
        command_str = config.namespace_sep.join(namespace)
        arg_str = " ".join(f"[{arg.helper()}]" for arg in command.parser.args.values())

    help_text += section("usage", f"{root.name} {command_str} {arg_str}")

    if command.doc.doc:
        help_text += section("description", command.doc.description)
        for heading, content in command.doc.sections.items():
            help_text += section(heading, content)

    if command.subcommands:
        name_size = len(max(command.subcommands.keys(), key=len))

        help_text += section(
            "subcommands",
            [
                f"{fg.ARC_BLUE}{sub.name:<{name_size}}{effects.CLEAR}   "
                + f"{sub.doc.description}"
                for sub in command.subcommands.values()
            ],
        )

    print(help_text)
