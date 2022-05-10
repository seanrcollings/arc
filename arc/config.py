import typing as t
from dataclasses import dataclass, field
import arc.typing as at
from arc.color import fg
from arc import logging
from arc.prompt import Prompt


@dataclass
class Config:
    """Arc Config object. All arguments have default values,
    so the configuration file is not required by default"""

    environment: at.Env = "production"
    default_section_name: str = "description"
    transform_snake_case: bool = True
    brand_color: str = fg.ARC_BLUE
    suggestions: at.Suggestions = field(  # type: ignore
        default_factory=lambda: {
            "suggest_params": True,
            "suggest_commands": True,
            "distance": 2,
        }
    )
    env_prefix: str = ""
    prompt: Prompt = Prompt(" ")
    version: t.Optional[str] = None
    autocomplete: bool = False


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
):
    """Function for updating global `arc` configuration

    Args:
        version: Version string to display with `--version`

        environment: The current environment, either `production` or `development`.
            Defaults to `production`. When in `development` mode, debug
            information is printed during execution.

        default_section_name: The name to use by default if the first section in a
            command docstring is does not have a header. Defaults to `description`.

        transform_snake_case:  Transform `snake_case` to `kebab-case`.
            Defaults to `True`.

        brand_color: Highlight color to use in help documentation.
            Defaults to `fg.ARC_BLUE`.

        env_prefix: A prefix to use when selecting values from environmental
                variables. Will be combined with the name specified for a parameter.

        prompt: A prompt object will be used when prompting
            for parameter values. Is also made available via `Context.prompt`.

        autocomplete: Enable / disable command line completions for this app. Currently
            the default is `False`
    """
    data = {
        "version": version,
        "environment": environment,
        "default_section_name": default_section_name,
        "transform_snake_case": transform_snake_case,
        "brand_color": brand_color,
        "suggestions": config.suggestions | (suggestions or {}),
        "env_prefix": env_prefix,
        "prompt": prompt,
        "autocomplete": autocomplete,
    }

    for key, value in data.items():
        if value is not None:
            setattr(config, key, value)

    if environment:
        logging.root_setup(environment)
