from __future__ import annotations
import typing as t
from dataclasses import dataclass, field
from arc import logging
import arc.typing as at
from arc.color import fg
from arc.prompt import Prompt
from arc.logging import logger, mode_map


@dataclass
class Config:
    """arc's Config object. A single global instance
    of this class is created, then used where it is needed"""

    environment: at.Env = "production"
    default_section_name: str = "description"
    transform_snake_case: bool = True
    brand_color: str = fg.ARC_BLUE
    env_prefix: str = ""
    prompt: Prompt = Prompt(" ")
    version: t.Optional[str] = None
    autocomplete: bool = False
    allow_unrecognized_args: bool = False
    autoload_overwrite: bool = True
    debug: bool = False
    suggestions: at.Suggestions = field(
        default_factory=lambda: at.Suggestions(
            suggest_params=True,
            suggest_commands=True,
            distance=2,
        )
    )


config = Config()


def configure(
    version: t.Optional[str] = None,
    environment: t.Optional[at.Env] = None,
    default_section_name: t.Optional[str] = None,
    transform_snake_case: t.Optional[bool] = None,
    brand_color: t.Optional[str] = None,
    suggestions: t.Optional[at.Suggestions] = None,
    env_prefix: t.Optional[str] = None,
    prompt: t.Optional[Prompt] = None,
    autocomplete: t.Optional[bool] = None,
    allow_unrecognized_args: t.Optional[bool] = None,
    autoload_overwrite: bool | None = None,
    debug: bool | None = None,
):
    """Function for updating global `arc` configuration

    Args:
        version: Version string to display with `--version`

        environment: The current environment, either `production` or `development`.
            Defaults to `production`. When in `development` mode, the arc logger is set
            to level `logging.INFO`

        default_section_name: The name to use by default if the first section in a
            command docstring is does not have a header. Defaults to `description`.

        transform_snake_case:  Transform `snake_case` to `kebab-case`.
            Defaults to `True`.

        brand_color: Highlight color to use in help documentation.
            Defaults to `fg.ARC_BLUE`.

        env_prefix: A prefix to use when selecting values from environmental
                variables. Will be combined with the name specified by parameter.

        prompt: A prompt object will be used when prompting
            for parameter values. Is also made available via `Context.prompt`.

        autocomplete: Enable / disable command line completions for this app. Currently
            the default is `False`

        allow_unrecognized_args: arc will not error when there are arguments provided
            that arc does not recognize. Their values will be stored in the context under the
            key `arc.parse.extra`. Defaults to `False`

        autoload_overwrite: allow / disallow a command that has been autoloaded to overwrite
            a pre-existing command object. Defaults to `True`

        debug: enable / disable arc debug logs.
    """
    data: dict = {
        "version": version,
        "environment": environment,
        "default_section_name": default_section_name,
        "transform_snake_case": transform_snake_case,
        "brand_color": brand_color,
        "suggestions": config.suggestions | (suggestions or {}),  # type: ignore
        "env_prefix": env_prefix,
        "prompt": prompt,
        "autocomplete": autocomplete,
        "allow_unrecognized_args": allow_unrecognized_args,
        "autoload_overwrite": autoload_overwrite,
        "debug": debug,
    }

    for key, value in data.items():
        if value is not None:
            setattr(config, key, value)

    if debug:
        logger.setLevel(logging.DEBUG)
    elif env := data["environment"]:
        logger.setLevel(mode_map.get(env, logging.WARNING))  # type: ignore
