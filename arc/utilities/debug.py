import os

from arc import namespace, arc_config
from arc.convert import converter_mapping
from arc.present import Table, Box

debug = namespace("debug")


@debug.subcommand()
def config():
    """Displays information about the current config of the Arc app"""
    config_items = [
        ["Namespace Seperator", arc_config.namespace_sep, ":"],
        ["Argument Assignment", arc_config.arg_assignment, "="],
        ["Flag Denoter", arc_config.flag_denoter, "--"],
        ["Log", arc_config.loglevel, "logging.WARNING"],
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
