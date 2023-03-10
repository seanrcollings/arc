from __future__ import annotations
import typing as t
from dataclasses import dataclass, field
from arc import logging
import arc.typing as at
from arc.color import fg
from arc.prompt import Prompt
from arc.logging import logger, mode_map

if t.TYPE_CHECKING:
    from arc.types.semver import SemVer


@dataclass
class LinksConfig:
    """Configures Links for the application"""

    bug: str | None = None


@dataclass
class SuggestionConfig:
    """Configures Suggestiosn for the application"""

    commands: bool = True
    params: bool = True
    distance: int = 2


@dataclass
class ColorConfig:
    """Configures Colors for the application"""

    error: str = fg.RED
    highlight: str = fg.YELLOW
    accent: str = fg.ARC_BLUE
    subtle: str = fg.GREY


@dataclass
class Config:
    """arc's Config object. A single global instance
    of this class is created, then used where it is needed"""

    environment: at.Env = "production"
    default_section_name: str = "description"
    transform_snake_case: bool = True
    env_prefix: str = ""
    version: str | SemVer | None = None
    autocomplete: bool = False
    allow_unrecognized_args: bool = False
    autoload_overwrite: bool = True
    debug: bool = False
    prompt: Prompt = field(default_factory=Prompt)
    suggest: SuggestionConfig = field(default_factory=SuggestionConfig)
    color: ColorConfig = field(default_factory=ColorConfig)
    links: LinksConfig = field(default_factory=LinksConfig)


config = Config()


def configure(
    *,
    version: str | None = None,
    environment: at.Env | None = None,
    default_section_name: str | None = None,
    transform_snake_case: bool | None = None,
    suggest: SuggestionConfig | None = None,
    env_prefix: str | None = None,
    prompt: Prompt | None = None,
    autocomplete: bool | None = None,
    allow_unrecognized_args: bool | None = None,
    autoload_overwrite: bool | None = None,
    debug: bool | None = None,
    color: ColorConfig | None = None,
    links: LinksConfig | None = None,
):
    """Function for updating global `arc` configuration

    Args:
        version (str | SemVer, optional): Version string to display with `--version`

        environment (str, optional): The current environment, either `production` or `development`.
            Defaults to `production`. When in `development` mode, the arc logger is set
            to level `logging.INFO`

        default_section_name (str, optional): The name to use by default if the first section in a
            command docstring is does not have a header. Defaults to `description`.

        transform_snake_case (bool, optional):  Transform `snake_case` to `kebab-case`.
            Defaults to `True`.

        env_prefix (str, optional): A prefix to use when selecting values from environmental
                variables. Will be combined with the name specified by parameter.

        prompt (Prompt, optional): A prompt object will be used when prompting
            for parameter values. Is also made available via `Context.prompt`.

        autocomplete (bool, optional): Enable / disable command line completions for this app. Currently
            the default is `False`

        allow_unrecognized_args (bool, optional): arc will not error when there are arguments provided
            that arc does not recognize. Their values will be stored in the context under the
            key `arc.parse.extra`. Defaults to `False`

        autoload_overwrite (bool, optional): allow / disallow a command that has been autoloaded to overwrite
            a pre-existing command object. Defaults to `True`

        debug (bool, optional): enable / disable arc debug logs.

        color (ColorConfig, optional): set the color configuration used throughout the application

        suggest (SuggestConfig, optional): configure the settings for suggesting replacements when
            arc does not recognize a command / parameter

        links (LinksConfig, optional): configure the links that arc may use in some output
    """
    data: dict = {
        "version": version,
        "environment": environment,
        "default_section_name": default_section_name,
        "transform_snake_case": transform_snake_case,
        "suggestions": suggest,
        "env_prefix": env_prefix,
        "prompt": prompt,
        "autocomplete": autocomplete,
        "allow_unrecognized_args": allow_unrecognized_args,
        "autoload_overwrite": autoload_overwrite,
        "debug": debug,
        "color": color,
        "links": links,
    }

    for key, value in data.items():
        if value is not None:
            setattr(config, key, value)

    if debug:
        logger.setLevel(logging.DEBUG)
    elif env := data["environment"]:
        logger.setLevel(mode_map.get(env, logging.WARNING))
