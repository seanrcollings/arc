import logging
from typing import Generic, TypeVar, Union, Any

from arc.convert.converters import *

T = TypeVar("T")


class ConfigValue(Generic[T]):
    def __init__(self, kind: type, default: Optional[T] = None):
        self.name = ""
        self.kind = getattr(kind, "__origin__", kind)
        self.default = default

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        value = getattr(obj, f"_{self.name}", None)

        # Work around for setting the default value
        # on the class
        if (not value) and self.default:
            self.__set__(obj, self.default)
            return self.default
        return value

    def __set__(self, obj, value: T):
        value = self._pre_set(value)
        self.__set_value(obj, value)

    def __set_value(self, obj, value: T):
        if not isinstance(value, self.kind):
            raise TypeError(
                (
                    f"Config {self.name} must be of type: "
                    f"{self.kind.__name__}, "
                    f"given: {type(value).__name__}"
                )
            )

        setattr(obj, f"_{self.name}", value)
        self._post_set(value)

    def _pre_set(self, value: Any):
        return value

    def _post_set(self, value: T):
        """Used to check / process self.value
        should be defined in subclass
        """


class ManagedLogging(ConfigValue[int]):
    value: int
    LOG_MAPPING = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    def __init__(self, logger_name: str, default: int = 30):
        self.logger_name = logger_name
        super().__init__(int, default)

    def __set__(self, obj, value: Union[int, str]):
        if isinstance(value, int):
            setattr(obj, f"_{self.name}", value)
            self._post_set(value)
        else:
            if log_value := self.LOG_MAPPING.get(value.upper()):
                self.value = log_value
            else:
                super().__set__(obj, value)  # type: ignore

    def _post_set(self, value):
        logger = logging.getLogger(self.logger_name)

        if value not in self.LOG_MAPPING.values():
            raise ValueError(f"`{value}` not a valid logging level")

        logger.setLevel(value)
