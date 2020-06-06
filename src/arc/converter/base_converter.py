import sys
from abc import ABC, abstractmethod, abstractclassmethod
from arc.converter import ConversionError


class BaseConverter(ABC):
    '''Base Converter, all converters must inherit from this converter'''
    def __new__(cls, value):
        return cls.try_convert(value)

    @abstractclassmethod
    def convert(cls, value: str):
        ''' Method that converts the string sent, to it's desired type.'''

    @property
    @abstractmethod
    def convert_to(self):
        ''' Specifies conversion type

        String that specifies what type the
        converter is supposed to convert the
        value into
        '''

    @classmethod
    def try_convert(cls, value: str):
        ''' Try except wrapper for conversion method

        Convert method wrapper for catching
        ConversionErrors. Will display the info
        passed to the ConversionError by the
        converter
        '''
        try:
            value = cls.convert(value)

        except ConversionError as e:
            print(f"'{e.value}' could not be converted to '{cls.convert_to}'")
            if e.helper_text is not None:
                print(e.helper_text)
            sys.exit(1)

        return value
