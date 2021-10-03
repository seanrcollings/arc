import os
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import get_type_hints
from arc import errors


class ConfigBase:
    ENV_PREFIX: str = ""

    def from_file(self, filename: str, required: bool = False) -> bool:
        """Load configuration attributes from a file

        Args:
            filename: the file to read
            required: whether or not a missing file raises an exception

        Raises:
            ArcError: if required is `True` and the file does not exist
        """
        config_file = Path(filename).expanduser().resolve()

        if not config_file.is_file():
            if not required:
                return False
            raise errors.ArcError(f"File '{filename}' does not exist / is not a file")

        file = config_file.open()
        lines = [
            stripped
            for line in file.readlines()
            if (stripped := line.partition("#")[0].strip("\n")) != ""
        ]
        file.close()

        parsed = self.parse(lines)
        self.set_values(parsed)
        return True

    def from_env(self, prefix: str = None, upper: bool = True):
        """Loads configuration attributes from environment variables

        Args:
            prefix: an optional common prefix for all env configuration options.
                For example, if the attribute is `mode` the prefix is `arc_` and the
                enviroment variable would be expected to be `arc_mode`
            upper: whether to assume that the environment variable is uppercase, defaults
                to `True`
        """
        prefix = prefix or self.ENV_PREFIX
        attrs = [a for a in vars(self) if not a.startswith("__")]
        values: dict = {}
        for attr in attrs:
            name = f"{prefix}{attr}"
            if upper:
                name = name.upper()

            if value := os.getenv(name):
                values[attr] = value

        self.set_values(values)

    def parse(self, lines: list[str]):
        """Parses the configuration file

        Args:
            lines (list[str]): Lines of the file

        Raises:
            errors.ArcError: If the config does not follow a `key=value` format

        Returns:
            `dict[str, any]`: Dictionary of key-value pairs loaded
        """
        parsed = {}
        try:
            for line in lines:
                key, value = line.split("=")
                parsed[key] = self.__convert_loaded_value(key, value)
        except Exception as e:
            breakpoint()
            raise errors.ArcError(
                "Config values must follow the form `name=value`"
            ) from e

        return parsed

    def set_values(self, values: dict):
        """Handles setting the config values from a dictionary

        Args:
            values (dict): Data returned by `parse()`

        Raises:
            errors.ArcError: If an item in the dictionary doesn't exist on the config object
        """
        for key, value in values.items():
            if not hasattr(self, key):
                raise errors.ArcError(f"Cannot set `{key}`")

            setattr(self, key, value)

        self.post_load()

    def __convert_loaded_value(self, name: str, value: str):
        # pylint: disable=import-outside-toplevel
        from arc.types import type_store

        annotation = get_type_hints(self)[name]
        converter = type_store.get_converter(annotation)
        return converter(annotation).convert(value)

    def post_load(self):
        """Executed after a loading a config from file or from env
        for post-load setup
        """


@dataclass
class Config(ConfigBase):
    """Arc Config object. All arguments have default values,
    so the configuration file is not required by default"""

    ENV_PREFIX = "ARC_"
    namespace_sep: str = ":"
    """Character to seperate command names: `parent:child:granchild`"""
    arg_assignment: str = "="
    """Character to seperate argument names from argument values
    when parsing via keyword `name=value`"""
    flag_denoter: str = "--"
    """Characters the proceed a flag argument: `--flag`"""
    short_flag_denoter: str = "-"
    """Characters that proceed a shortened flag `-f`"""
    mode: str = "production"
    """The current mode of the application, possible values:
    - production
    - development
    - test
    """
    suggest_on_missing_argument: bool = True
    """Wether or not to provide suggestions for possible misspellings
    when an argument is not found"""

    suggest_on_missing_command: bool = True
    """Wether or not to provide suggestions for possible misspellings
    when a command is not found"""

    suggest_levenshtein_distance: int = 2
    """The max Levenshtein distance between input and a
    possible correction to trigger a suggestion """

    default_section_name: str = "description"
    """The name to use by default if the first section
    in a command docstring is anonymous
    """

    parse_argument_help: bool = False
    """Wether or not to attempt to parse the argument
    section of help documentation to provide better documentation"""

    tranform_snake_case: bool = True
    """Transforms snake_case argument names to kebab-case. Defaults to True"""

    color: bool = True
    """Use Ansi-escape sequences. Defaults to true"""

    mode_map = {
        "development": logging.DEBUG,
        "production": logging.WARNING,
        "test": logging.ERROR,
    }


config = Config()
