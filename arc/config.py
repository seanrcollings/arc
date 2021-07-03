import os
from dataclasses import dataclass
import logging
from pathlib import Path
from arc import errors


class ConfigBase:
    ENV_PREFIX: str = ""
    last_loaded: str = ""

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

        if str(config_file) == self.last_loaded:
            return True

        self.last_loaded = str(config_file)
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
                parsed[key] = value
        except Exception as e:
            raise errors.ArcError(
                "Config values must follow the form `name=value`"
            ) from e

        return parsed

    def set_values(self, parsed: dict):
        """Handles setting the parsed config data

        Args:
            parsed (dict): Data returned by `parse()`

        Raises:
            errors.ArcError: If an item in the dictionary doesn't exist on the config object
        """
        for key, value in parsed.items():
            if not hasattr(self, key):
                raise errors.ArcError(f"Cannot set `{key}`")

            setattr(self, key, self.__convert_loaded_value(value))

        self.post_load()

    def __convert_loaded_value(self, value: str):
        """Attempts to convert a loaded config value, if it
        cannot, will return the original string"""

        # Check if it needs to be converted
        # pylint: disable=import-outside-toplevel
        from arc.convert import converters, BaseConverter

        config_converters: tuple[type[BaseConverter], ...] = (
            converters.IntConverter,
            converters.BoolConverter,
            converters.FloatConverter,
        )

        for converter in config_converters:
            try:
                return converter().convert(value)
            except errors.ConversionError:
                continue

        return value

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

    mode_map = {
        "development": logging.DEBUG,
        "production": logging.WARNING,
        "test": logging.ERROR,
    }


config = Config()
