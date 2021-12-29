import os
from pprint import pprint

from arc import namespace, Context
from arc.config import config, Config
from arc.types import aliases
from arc.present import Table, Box

debug = namespace("debug", description="debug utilties for an arc application")


@debug.subcommand("config")
def config_command():
    """Displays information about the current config of the arc app"""
    config_items = [
        [name, getattr(config, name), value.default]
        for name, value in Config.__dataclass_fields__.items()  # pylint: disable=no-member
    ]

    table = Table(
        columns=[{"name": "NAME", "width": 30}, "VALUE", "DEFAULT"], rows=config_items
    )
    print(Box(str(table), justify="center", padding=1))


@config_command.subcommand("file")
def config_to_file():
    """Outputs the current configuration in .arc file format"""
    config_items = [
        [name, getattr(config, name)]
        for name in Config.__dataclass_fields__  # pylint: disable=no-member
    ]
    print("\n".join(f"{name}={value}" for name, value in config_items))


@debug.subcommand("aliases")
def aliases_c():
    """Displays information aboubt the currently accessible type aliases"""

    table = Table(
        columns=[
            {"name": "ALIAS", "justify": "left", "width": 20},
            {"name": "TYPE", "justify": "right", "width": 40},
        ],
        rows=[[v.__name__, k] for k, v in aliases.Alias.aliases.items()],
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


@debug.subcommand()
def schema(ctx: Context):
    """Prints out a dictionary representation of the CLI"""
    print(ctx.root.command.schema())
