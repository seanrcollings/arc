import os

from arc import namespace, config
from arc.convert import converter_mapping
from arc.present import Table, Box

debug = namespace("debug")


@debug.subcommand("config")
def config_command():
    """Displays information about the current config of the Arc app"""
    config_items = [
        ["Namespace Seperator", config.namespace_sep, ":"],
        ["Argument Assignment", config.arg_assignment, "="],
        ["Flag Denoter", config.flag_denoter, "--"],
        ["Mode", config.mode, "production"],
        ["Converters", "See debug:converters", "-"],
    ]

    table = Table(columns=["NAME", "VALUE", "DEFAULT"], rows=config_items)
    print(Box(str(table), justify="center", padding=1))


@debug.subcommand()
def converters():
    """Displays information aboubt the currently accessible converters"""
    table = Table(
        columns=[
            {"name": "Converter Name", "justify": "center"},
        ],
        rows=[[v.__name__] for v in converter_mapping.values()],
    )
    print(Box(str(table), justify="center", padding=1))


@debug.subcommand()
def arcfile():
    """Prints the contents of the .arc file in the CWD"""
    if os.path.isfile(".arc"):
        file = open(".arc")
        print(".arc file contents: ")
        print(file.read())
        file.close()
    else:
        print(".arc file does not exist")
