import os
import random

from arc import namespace, config
from arc.formatters import Table, Box

debug = namespace("debug")


@debug.subcommand("config")
def display_config():
    """Displays information about the current config of the Arc app"""
    config_items = [
        ["Namespace Seperator", config.namespace_sep, ":"],
        ["Argument Assignment", config.arg_assignment, "="],
        ["Flag Denoter", config.flag_denoter, "--"],
        ["Log", config.loglevel, "logging.WARNING"],
        ["Converters", "See debug:converters", "-"],
    ]

    table = Table(
        headers=["name", "value", "default"], rows=config_items, column_width=25
    )
    print(Box(str(table)))


@debug.subcommand("converters")
def converters():
    """Displays information aboubt the currently accessible converters"""
    filler_words = ["foo", "bar", "baz", "buzz"]  # Randomly pick for filler information
    converter_rows = [
        [v.__name__, v.convert_to, f"{random.choice(filler_words)} : {k}"]
        for (k, v) in config.converters.items()
    ]

    table = Table(
        headers=["Converter Name", "Convert to", "Example"],
        rows=converter_rows,
        column_width=30,
    )
    print(Box(str(table)))


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
