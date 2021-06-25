import os
from dataclasses import dataclass
import logging
from pathlib import Path
from arc import errors
from arc.logging import logger


class ConfigBase:
    ENV_PREFIX: str = ""
    last_loaded: str = ""

    def from_file(self, filename: str, required: bool = False):
        """Load configuration attributes from a file

        :param filename: the file to read
        :param required: whether or not a missing file raises an exception
        """
        config_file = Path(filename).expanduser().resolve()

        if not config_file.is_file():
            if not required:
                return
            raise errors.ArcError(f"File '{filename}' does not exist / is not a file")

        if str(config_file) == self.last_loaded:
            return

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

    def from_env(self, prefix: str = None, upper: bool = True):
        """Loads configuration attributes from environment variables

        :param prefix: an optional common prefix for all env configuration options.
        For example, if the attribute is `mode` the prefix is `arc_` and the
        enviroment variable would be expected to be `arc_mode`
        :param upper: whether to assume that the environment variable is uppercase, defaults
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
        ...


@dataclass
class Config(ConfigBase):
    ENV_PREFIX = "ARC_"
    namespace_sep: str = ":"
    arg_assignment: str = "="
    flag_denoter: str = "--"
    mode: str = "production"
    loglevel: int = 30

    def __post_init__(self):
        self.post_load()

    def post_load(self):
        mode_map = {
            "development": logging.DEBUG,
            "production": logging.INFO,
            "test": logging.ERROR,
        }
        level = mode_map.get(self.mode, self.loglevel)
        self.loglevel = level
        logger.setLevel(level)


config = Config()
