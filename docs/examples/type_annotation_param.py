from typing import Annotated
import pathlib
import arc

ConfigPathParam = Annotated[
    pathlib.Path,
    arc.Option(name="config", short="c", desc="The configuration file path."),
]


@arc.command
def hello(config_path: ConfigPathParam):
    arc.print(config_path, type(config_path))


hello()
