import os

from arc import namespace
from arc.config import config, Config
from arc.types import param_types
from arc.present import Table, Box

debug = namespace("debug")


@debug.subcommand("config")
def config_command():
    """Displays information about the current config of the Arc app"""
    config_items = [
        [name, getattr(config, name), value.default]
        for name, value in Config.__dataclass_fields__.items()  # pylint: disable=no-member
    ]

    table = Table(
        columns=[{"name": "NAME", "width": 30}, "VALUE", "DEFAULT"], rows=config_items
    )
    print(Box(str(table), justify="center", padding=1))


@debug.subcommand()
def types():
    """Displays information aboubt the currently accessible types"""

    table = Table(
        columns=[
            {"name": "NAME", "justify": "left"},
            {"name": "TYPE", "justify": "left", "width": 40},
            {"name": "PARAM TYPE", "justify": "right", "width": 40},
        ],
        rows=[
            [v.name, k, v.__name__]
            for k, v in param_types.ParamType._param_type_map.items()
        ],
    )
    # print(Box(str(table), justify="center", padding=1))
    print(table)


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
