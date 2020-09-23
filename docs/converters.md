# Type Converters
- [Type Converters](#type-converters)
  - [Builtin Converters](#builtin-converters)
  - [Future Converters](#future-converters)
  - [Use](#use)
  - [Examples](#examples)
    - [Int Conversion](#int-conversion)
    - [Float Converion](#float-converion)
  - [Custom Converters](#custom-converters)
  - [Input Converter Functions](#input-converter-functions)




## Builtin Converters
| Indicator | Class Name      | Converts          | Conversion Method               |
| --------- | --------------- | ----------------- | ------------------------------- |
| str       | StringConverter | name=Jonathen     | python builtin `str()`          |
| byte      | ByteConverter   | name=Terry        | python builtin `str.encode()`   |
| int       | IntConverter    | number=4          | python builtin `int()`          |
| float     | FloatConverter  | number=3.5        | python builtin `float()`        |
| list      | ListConverter   | my_list=1,2,3,4,5 | Splits on commas, strips spaces |

## Future Converters
| Indicator | Class Name    | Converts                    | Conversion Method |
| --------- | ------------- | --------------------------- | ----------------- |
| dict      | DictConverter | my_dict=key:value,key:value | ?                 |


## Use
Typically, you don't want numbers, booleans, lists, represented as just strings. Arc provides type conversions that will convert the input to your desired type before passing it on to the script. If you've used Flask before, it's URL converters way in essentially the same way. If no converter is specified, the StringConverter is used by default.

The type to convert input to is specified by Python's builin type hinting system

## Examples
### Int Conversion
```py
@cli.script("number_type")
def number_type(number: int):
    '''Prints the type of a number'''
    print(type(number))
```

```out
$ python3 example.py number_type number=5
<class 'int'>
```

### Float Converion
```py
@cli.script("float_type")
def float_type(number: float):
    '''Prints the type of a float'''
    print(type(number))
```

```out
$ python3 example.py number_type number=5.3
<class 'float'>
```
Check [examples/converters.py](/examples/converters.py) for full examples

## Custom Converters
Arc also allows you to add your own custom converters

```py
from arc.convert import BaseConverter, ConversionError

class CustomObject:
  # ...

class CustomObjectConverter(BaseConverter):
  convert_to = CustomObject

  def convert(self, value):
    # ...
    # if conversion fails, raise a conversion error
    # return converted object
```
A converter class must define:
- `convert_to`: Nmae of the object the converter is meant to convert to
- `convert`: the method that does the converting. Returns an instance of the convert_to object
  - Must accept one paramter, which is whatever the user input for that option

To add a converter to the list of available ones:
```py
from arc import Config
cli = CLI()
Config.add_converter(CircleConverter)
```

See a full example in [examples/custom_converter.py](/examples/custom_converter.py)

Pre-made converters defined in [src/arc/converter/converters.py](/src/arc/converter/converters.py)

## Input Converter Functions
Arc also allows you to use it's converter functionality when gathering user input from within a script
```py
from arc import CLI
from arc.convert.input import convert_to_int

cli = CLI()

@cli.script("example")
def example():
  cool_number = convert_to_int("Please enter a number: ")
  print(type(cool_number)) # '<class : int>'

cli()
```
Note that all convereters in `Config.converter` will have a function associated with it. This includes all custom converters. The functions will be named `convert_to_<indicator>`

Note that if the script defines a custom converter, it's respective input function will need to be imported after it is added to `Config.converter` otherwise it doesn't yet exist to import.