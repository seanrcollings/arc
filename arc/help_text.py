from arc.command import Command, ParsingMethod
from arc.command.argument import Argument
from arc.command.command_doc import CommandDoc
from arc.color import fg, effects
from arc.config import config
from arc.run import find_command

__all__ = ["display_help", "generate_help"]


def display_help(root: Command, command: Command, namespace: list[str]):
    print(generate_help(root, command, namespace))


def generate_help(root: Command, command: Command, namespace: list[str]) -> str:
    generate_usage(command.doc, root, command, namespace)
    generate_aliases(command.doc, root, command, namespace)
    generate_subcommands(command.doc, command)
    return str(command.doc)


def generate_usage(
    doc: CommandDoc,
    root: Command,
    command: Command,
    namespace: list[str],
):
    if command.is_namespace():
        return

    if root == command:
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


def generate_options_string(command: Command):
    format_strings = {
        ParsingMethod.STANDARD: f"{config.flag_denoter}{{name}} <...>",
        ParsingMethod.KEYWORD: f"{{name}}{config.arg_assignment}<...>",
        ParsingMethod.POSITIONAL: "<{name}>",
        "flag": f"{config.flag_denoter}{{name}}",
    }

    def format_single_arg(arg: Argument):
        format_string = (
            format_strings["flag"]
            if arg.is_flag()
            else format_strings[type(command.parser)]
        )
        arg_str = format_string.format(name=arg.name)
        if arg.is_optional():
            arg_str = f"[{arg_str}]"

        return arg_str

    args = []
    flags = []
    for arg in command.parser.args.values():
        formatted = format_single_arg(arg)
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
        lines = sub.doc.sections.get("description", "").split("\n")
        if len(lines) > 0:
            first_line = lines[0].strip("\n")
        else:
            first_line = ""
        subcommands += (
            f"{fg.ARC_BLUE}{sub.name:<{name_size}}{effects.CLEAR}   {first_line}\n"
        )

    doc.add_section("subcommands", subcommands)
