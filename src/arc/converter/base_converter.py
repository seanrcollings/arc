from arc.converter import ConversionError
import sys


class BaseConverter:
    def __new__(cls, value):
        return cls.try_convert(value)

    @property
    def convert(self):
        raise NotImplementedError(
            "Must Implement convert method in child class")

    @property
    def convert_to(self):
        raise NotImplementedError(
            "Must Implement convert_to string for documentation")

    @classmethod
    def try_convert(cls, value):
        try:
            value = cls.convert(value)

        except ConversionError as e:
            print(e)
            sys.exit(1)

        return value