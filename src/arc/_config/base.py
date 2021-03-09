from typing import Type, List, Optional, Any
from pathlib import Path

from arc.convert.converters import *
from arc.convert import BaseConverter
from arc.errors import ArcError, ConversionError


class ConfigBase:
    def __init__(self, **data):
        self.last_loaded: Optional[str] = None
        self.__set_values(data)

    def __set_values(self, data: Dict[str, Any]):
        for key, value in data.items():
            if not hasattr(self, key):
                raise ArcError(f"{self} has no attribute '{key}'")

            setattr(self, key, value)

    def from_file(self, filename: str, required: bool = False):
        config_file = Path(filename).expanduser().resolve()

        if not config_file.is_file():
            if not required:
                return
            raise ArcError(f"File '{filename}' does not exist / is not a file")

        if str(config_file) == self.last_loaded:
            return

        self.last_loaded = str(config_file)
        file = config_file.open()
        lines = list([line.partition("#")[0].strip("\n") for line in file.readlines()])
        file.close()

        parsed = self.parse(lines)
        self.set_values(parsed)

    def parse(self, lines: List[str]):
        # Have to do this for circular imports
        # pylint: disable=import-outside-toplevel
        from arc.parser import parse
        from arc.parser.data_types import KEY_ARGUMENT

        node = parse(" ".join(lines))
        parsed: dict[str, Any] = {}

        for arg in node.args:
            if arg.name is None or arg.kind != KEY_ARGUMENT:
                raise ArcError("Config values must follow the form `name=value`")
            parsed[arg.name] = self.__convert_loaded_value(arg.value)

        return parsed

    def set_values(self, parsed: dict):
        for key, value in parsed.items():
            if not hasattr(self, key):
                raise ArcError(f"Cannot set `{key}`")

            setattr(self, key, value)

    def __convert_loaded_value(self, value: str):
        """Attempts to convert a loaded config value, if it
        cannot, will return the original string"""

        # Check if it needs to be converted
        config_converters: List[Type[BaseConverter]] = [
            IntConverter,
            BoolConverter,
            FloatConverter,
            ListConverter,
        ]

        for converter in config_converters:
            try:
                return converter(converter.convert_to).convert(value)
            except ConversionError:
                continue

        return value
