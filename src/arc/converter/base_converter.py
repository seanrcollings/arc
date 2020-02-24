import sys
from arc.converter import ConversionError


class BaseConverter:
    '''Base Converter, all converters inherit from this converter'''
    def __new__(cls, value):
        return cls.try_convert(value)

    @classmethod
    def convert(cls, value: str):
        ''' Method that converts the string sent, to it's desired type.
        Must implement in child class
        '''
        raise NotImplementedError(
            "Must Implement convert method in child class")

    @property
    def convert_to(self):
        ''' Specifies conversion type

        String that specifies what type the
        converter is supposed to convert the
        value into
        '''
        raise NotImplementedError(
            "Must Implement convert_to string in child class")

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
