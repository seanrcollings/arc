from dataclasses import dataclass
import arc.typing as at
from arc.color import fg
from arc import logging


@dataclass
class Config:
    """Arc Config object. All arguments have default values,
    so the configuration file is not required by default"""

    environment: at.Env = "production"
    default_section_name: str = "description"
    transform_snake_case: bool = True
    brand_color: str = fg.ARC_BLUE


config = Config()


def configure(
    environment: at.Env = None,
    default_section_name: str = None,
    transform_snake_case: bool = None,
    brand_color: str = None,
):
    """Function for updating global `arc` configuration

    - `environment`: The current environment, either `production` or `development`.
        Defaults to `production`. When in `development` mode, debug information
        is printed during execution.
    - `default_section_name`: The name to use by default if the first section in a
        command docstring is does not have a header. Defaults to `description`.
    - `transform_snake_case`: Transform `snake_case` to `kebab-case`. Defaults to `True`.
    - `brand_color`: Highlight color to use in help documentation. Defaults to `fg.ARC_BLUE`.
    """
    dictionary = {
        "environment": environment,
        "default_section_name": default_section_name,
        "transform_snake_case": transform_snake_case,
        "brand_color": brand_color,
    }

    for key, value in dictionary.items():
        if value is not None:
            setattr(config, key, value)

    if environment:
        logging.root_setup(environment)
