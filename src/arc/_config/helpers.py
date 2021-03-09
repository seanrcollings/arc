import logging
from typing import Generic, TypeVar, Union, Any

from arc.convert.converters import *

T = TypeVar("T")


class ConfigValue(Generic[T]):
    def __init__(self):
        self.name = ""

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return getattr(obj, f"_{self.name}", None)

    def __set__(self, obj, value: Any):
        converted = self._pre_set(value)
        value = self.__get__(obj)

        if value is not None:
            if not isinstance(converted, type(value)):
                raise TypeError(
                    (
                        f"Config {self.name} must be of type: "
                        f"{type(value).__name__}, "
                        f"given: {type(converted).__name__}"
                    )
                )

        setattr(obj, f"_{self.name}", converted)
        self._post_set(converted)

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

    def __init__(self, logger_name: str):
        self.logger_name = logger_name
        super().__init__()

    def __set__(self, obj, value: Union[int, str]):
        if isinstance(value, int):
            setattr(obj, f"_{self.name}", value)
            self._post_set(value)
        else:
            if log_value := self.LOG_MAPPING.get(value.upper()):
                self.value = log_value
            else:
                super().__set__(obj, value)

    def _post_set(self, value):
        logger = logging.getLogger(self.logger_name)

        if value not in self.LOG_MAPPING.values():
            raise ValueError(f"`{value}` not a valid logging level")

        logger.setLevel(value)
