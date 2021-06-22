import os
import random

from arc import namespace, arc_config
from arc.present import Table, Box

debug = namespace("debug")


@debug.subcommand("config")
def display_config():
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


@debug.subcommand("converters")
def converters():
    """Displays information aboubt the currently accessible converters"""
    filler_words = ["foo", "bar", "baz", "buzz"]  # Randomly pick for filler information

    table = Table(
        columns=[
            "Converter Name",
            {"name": "Convert To", "width": 35},
            {"name": "Example", "justify": "right"},
        ],
        rows=[
            [v.__name__, v.convert_to, f"{random.choice(filler_words)} : {k}"]
            for (k, v) in arc_config.converters.items()
        ],
    )
    print(Box(str(table), justify="center", padding=1))


@debug.subcommand("arcfile")
def arcfile():
    """Prints the contents of the .arc file in the CWD"""
    if os.path.isfile(".arc"):
        file = open(".arc")
        print(".arc file contents: ")
        print(file.read())
        file.close()
    else:
        print(".arc file does not exist")
