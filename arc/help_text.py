import re
import textwrap

from arc.command import Command, ParsingMethod
from arc.command.argument import Argument
from arc.command.command_doc import CommandDoc
from arc.color import fg, effects, colorize
from arc.config import config
from arc.run import find_command
from arc import errors

__all__ = ["display_help", "generate_help"]


def display_help(root: Command, command: Command, namespace: list[str]):
    print(generate_help(root, command, namespace))


def generate_help(root: Command, command: Command, namespace: list[str]) -> str:
    generate_usage(command.doc, root, command, namespace)
    generate_aliases(command.doc, root, command, namespace)
    generate_subcommands(command.doc, command)
    if config.parse_argument_help:
        parse_argument_section(command.doc, command)
    return str(command.doc)


def generate_usage(
    doc: CommandDoc,
    root: Command,
    command: Command,
    namespace: list[str],
):
    if command.is_namespace():
        command_str = f"{command.name}{config.namespace_sep}<subcommand>"
        args_str = "[arguments ...]"
    elif root == command:
        command_str = "<command>"
        args_str = "[arguments ...]"
    else:
        command_str = config.namespace_sep.join(namespace)
        args_str = generate_options_string(command)

    doc.add_section(
        "usage",
        f"{fg.ARC_BLUE}{root.name}{effects.CLEAR}"
        f" {effects.UNDERLINE}{command_str}{effects.CLEAR} {args_str}",
    )


def format_arg(arg: Argument, command: Command, short: bool = False):
    flag_denoter = config.short_flag_denoter if short else config.flag_denoter
    format_strings = {
        ParsingMethod.STANDARD: f"{flag_denoter}{{name}}",
        ParsingMethod.KEYWORD: f"{{name}}{config.arg_assignment}",
        ParsingMethod.POSITIONAL: "<{name}>",
    }

    format_string = (
        format_strings[ParsingMethod.STANDARD]
        if arg.is_flag()
        else format_strings[type(command.parser)]
    )
    name = arg.short if short else arg.name
    arg_str = format_string.format(name=name.replace("_", "-"))

    return arg_str


def format_usage_arg(arg: Argument, command: Command):
    formatted = format_arg(arg, command)
    if (
        isinstance(command.parser, (ParsingMethod.KEYWORD, ParsingMethod.STANDARD))
        and not arg.is_flag()
    ):
        formatted += " <...>"

    if arg.is_optional():
        formatted = f"[{formatted}]"

    return formatted


def generate_options_string(command: Command):
    args = []
    flags = []
    for arg in (arg for arg in command.parser.args.values() if not arg.hidden):
        formatted = format_usage_arg(arg, command)
        if arg.is_flag():
            flags.append(formatted)
        else:
            args.append(formatted)

    return " ".join(args + flags)


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
        subcommands += (
            f"{fg.ARC_BLUE}{sub.name:<{name_size}}"
            f"{effects.CLEAR}   {sub.doc.short_description}\n"
        )

    doc.add_section("subcommands", subcommands)


# TODO: Cleanup this function, it's super clunky as is
def parse_argument_section(doc: CommandDoc, command: Command):
    arguments_str = doc.sections.get("arguments")
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
            f"of {command.name}'s documentation does not follow the "
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
        argument = command.parser.args.get(name)
        if not argument:
            raise errors.ParserError(
                f"Argument section Parsing failed. No arg named {name}"
            )

        formatted_name = format_arg(argument, command)
        if argument.short:
            formatted_name += f" ({format_arg(argument, command, True)})"
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

    doc.add_section("arguments", formatted_str)
