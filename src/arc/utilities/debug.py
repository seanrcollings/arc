import os
import random

from arc import Utility, Config
from arc.utilities.__table import Table

debug = Utility("debug")


@debug.script("config")
def config():
    '''Displays information about the current config of the Arc app'''
    config_items = [["Decorate Text", Config.decorate_text, "True"],
                    ["Utility Seperator", Config.utility_seperator, ":"],
                    ["Options Seperator", Config.options_seperator, "="],
                    ["Log", Config.log, "False"],
                    ["Debug", Config.debug, "False"],
                    ["Converters", "See debug:converters", "N/A"]]

    table = Table(headers=["name", "value", "default"],
                  rows=config_items,
                  column_width=25)
    table.print_table()


@debug.script("converters")
def converters():
    '''Displays information about the currently accessible converters'''
    filler_words = ["foo", "bar", "baz",
                    "buzz"]  # Randomly pick for filler information
    converter_rows = [[
        v.__name__, v.convert_to, f"<{k}:{random.choice(filler_words)}>"
    ] for (k, v) in Config.converters.items()]

    table = Table(headers=["Converter Name", "Convert to", "Example"],
                  rows=converter_rows,
                  column_width=30)
    table.print_table()


@debug.script("arcfile")
def arcfile():
    '''Prints the contents of the .arc file in the CWD'''
    if os.path.isfile(".arc"):
        file = open(".arc")
        print(".arc file contents: ")
        print(file.read())
        file.close()
    else:
        print(".arc file does not exist")
