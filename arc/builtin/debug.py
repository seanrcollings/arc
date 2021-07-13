import os

from arc import namespace, config
from arc.types.type_store import type_store
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
            {"name": "TYPE", "justify": "left", "width": 40},
            {"name": "CONVERTER", "justify": "right"},
            {"name": "DISPLAY NAME", "justify": "right", "width": 30},
        ],
        rows=[
            [
                k,
                v["converter"].__name__,
                v["display_name"]
                if isinstance(v["display_name"], str)
                else "Context dependant",
            ]
            for k, v in type_store.items()
        ],
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
