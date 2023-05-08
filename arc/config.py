from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

import arc.typing as at

from arc.present.help_formatter import HelpFormatter, DefaultHelpFormatter
from arc.color import fg
from arc.prompt import Prompt

if t.TYPE_CHECKING:
    from arc.types.semver import SemVer
    from arc import Context


_config: Config | None = None


@dataclass
class ColorConfig:
    """Configures Colors for the application"""

    error: str = fg.RED
    highlight: str = fg.YELLOW
    accent: str = fg.ARC_BLUE
    subtle: str = fg.GREY


@dataclass
class PresentConfig:
    """Configures the presentation of the application"""

    indent: str = " " * 4
    """The indent to use for each level of indentation"""
    width: int = 80
    """The default width to present content at. This is used
    for wrapping text. Will be ignored if the terminal width is smaller"""
    color: ColorConfig = field(default_factory=ColorConfig)
    """The color configuration for the application"""
    formatter: type[HelpFormatter] = DefaultHelpFormatter
    """Class to use when formatting help messages"""


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
class PluginConfig:
    """Configures Plugins locations for the application"""

    paths: list[str] = field(default_factory=list)
    """List of paths to search for plugins. These paths will be searched
    for python  modules that contain a `plugin` function. If the file does
    not exist, or the function is not found, it will be ignored

    The paths provided can be to a specific file, or a directory. If a directory
    is provided, all files in that directory will be searched for plugins.
    """

    groups: list[str] = field(default_factory=lambda: ["arc.plugins"])
    """List of entrypoint groups to search for plugins. The entrypoint's value must be
    a callable that accepts a single argument, the `Context` object.

    Defaults to using the `arc.plugins` entrypoint group
    """

    entrypoints: list[str] = field(default_factory=list)
    """List of explicit entrypoints to search for plugins. The entrypoint's value must be
    a callable that accepts a single argument, the `Context` object.
    """


@dataclass
class Config:
    """arc's Config object. A single global instance
    of this class is created, then used where it is needed"""

    environment: at.Env = "production"
    transform_snake_case: bool = True
    env_prefix: str = ""
    version: str | SemVer | None = None
    autocomplete: bool = False
    allow_unrecognized_args: bool = False
    autoload_overwrite: bool = True
    debug: bool = False
    prompt: Prompt = field(default_factory=Prompt)
    suggest: SuggestionConfig = field(default_factory=SuggestionConfig)
    links: LinksConfig = field(default_factory=LinksConfig)
    present: PresentConfig = field(default_factory=PresentConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)

    @classmethod
    def load(cls) -> "Config":
        """Access the Global `Config` instance"""
        global _config

        if not _config:
            _config = cls()

        return _config

    def update(self, **kwargs: t.Any) -> None:
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

    @classmethod
    def __depends__(cls, ctx: Context) -> Config:
        return ctx.config


def configure(
    *,
    version: str | None = None,
    environment: at.Env | None = None,
    transform_snake_case: bool | None = None,
    suggest: SuggestionConfig | None = None,
    env_prefix: str | None = None,
    prompt: Prompt | None = None,
    autocomplete: bool | None = None,
    allow_unrecognized_args: bool | None = None,
    autoload_overwrite: bool | None = None,
    debug: bool | None = None,
    links: LinksConfig | None = None,
    present: PresentConfig | None = None,
    plugins: PluginConfig | None = None,
) -> None:
    """Function for updating global `arc` configuration

    Args:
        version (str | SemVer, optional): Version string to display with `--version`

        environment (str, optional): The current environment, either `production` or `development`.
            Defaults to `production`. When in `development` mode, the arc logger is set
            to level `logging.INFO`

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

        present (PresentConfig, optional): set the presentation configuration for arc

        suggest (SuggestConfig, optional): configure the settings for suggesting replacements when
            arc does not recognize a command / parameter

        links (LinksConfig, optional): configure the links that arc may use in some output
    """
    data: dict[str, t.Any] = {
        "version": version,
        "environment": environment,
        "transform_snake_case": transform_snake_case,
        "suggestions": suggest,
        "env_prefix": env_prefix,
        "prompt": prompt,
        "autocomplete": autocomplete,
        "allow_unrecognized_args": allow_unrecognized_args,
        "autoload_overwrite": autoload_overwrite,
        "debug": debug,
        "links": links,
        "present": present,
        "plugins": plugins,
    }

    config = Config.load()
    config.update(**data)
