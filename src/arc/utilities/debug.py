import os
import random

from arc import Utility, config
from arc.formatters.table import Table

debug = Utility("debug", "Various development-centric scripts")


@debug.script("config")
def display_config():
    """Displays information about the current config of the Arc app"""
    config_items = [
        ["Utility Seperator", config.utility_seperator, ":"],
        ["Options Seperator", config.options_seperator, "="],
        ["Log", config.loglevel, "logging.WARNING"],
        ["Anonymous Identifier", config.anon_identifier, "anon"],
        ["Converters", "See debug:converters", "-"],
    ]

    table = Table(
        headers=["name", "value", "default"], rows=config_items, column_width=25
    )
    print(table)


@debug.script("converters")
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
    print(table)


@debug.script("arcfile")
def arcfile():
    """Prints the contents of the .arc file in the CWD"""
    if os.path.isfile(".arc"):
        file = open(".arc")
        print(".arc file contents: ")
        print(file.read())
        file.close()
    else:
        print(".arc file does not exist")
