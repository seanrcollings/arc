# Type Converters
- [Type Converters](#type-converters)
  - [Builtin Converters](#builtin-converters)
  - [Future Converters](#future-converters)
  - [Use](#use)
  - [Examples](#examples)
    - [Int Conversion](#int-conversion)
    - [Float Converion](#float-converion)
  - [Custom Converters](#custom-converters)

Typically, you don't want numbers, booleans, lists, represented as just strings. Arc provides type conversions that will convert the input to your desired type before passing it on to the script. If you've used Flask before, it's URL converters way in essentially the same way
If no converter is specified, the StringConverter is used by default

## Builtin Converters
| Indicator | Class Name          | Converts          | Conversion Method                              |
| --------- | ------------------- | ----------------- | ---------------------------------------------- |
| str       | StringConverter     | name=Jonathen     | python builtin `str()`                         |
| byte      | ByteConverter       | name=Terry        | python builtin `str.encode()`                  |
| int       | IntConverter        | number=4          | python builtin `int()`                         |
| float     | FloatConverter      | number=3.5        | python builtin `float()`                       |
| bool      | BoolConverter       | happy=True, sad=0 | python builtin `bool()`                        |
| sbool     | StringBoolConverter | happy=True        | Looks for a string of True/true or False/false |
| ibool     | IntBoolConverter    | sad=0             | Truthy values of integers                      |
| list      | ListConverter       | my_list=1,2,3,4,5 | Splits on commas, strips spaces                |

## Future Converters
| Indicator | Class Name    | Converts                    | Conversion Method |
| --------- | ------------- | --------------------------- | ----------------- |
| dict      | DictConverter | my_dict=key:value,key:value | ?                 |


## Use
A converter is indicated using the same syntax as Flask's URL Converters `<type:varible_name>`
For example, for a int this could be: `<int:number>`
For a bool it could be: `<bool:go_left>`

## Examples
### Int Conversion
```py
@cli.script("number_type", options=["<int:number>"])
def number_type(number):
    '''Prints the type of a number'''
    print(type(number))
```

```
$ python3 example.py number_type number=5
<class 'int'>
```

### Float Converion
```py
@cli.script("float_type", options=["<float:number>"])
def float_type(number):
    '''Prints the type of a float'''
    print(type(number))
```

```
$ python3 example.py number_type number=5.3
<class 'float'>
```
Check [examples/converters.py](/examples/converters.py) for full examples

## Custom Converters
If you want to convert user input into your own custom object, or just modify the way that Arc alread does it, making custom converters is very easy.

```py
from arc.converter import BaseConverter, ConversionError

class CustomObject:
  # ...

class CustomObjectConverter(BaseConverter):
  convert_to = "CustomObject"

  @classmethod
  def convert(cls, value):
    # ...
    # if conversion fails, raise a conversion error
    # return converted object
```
A converter class must define:
- convert_to: string repr of the object the converter is meant to conver to
- convert: the method that does the converting. Returns an instance of the convert_to object
  - Must be a class method
  - Must accept one paramter, which is whatever the user input for that option

To add a converter to the list of available ones:
```py
cli = CLI()
cli.config.converters["custom"] = CustomObjectConverter # <custom:value>
```

See a full example in [examples/custom_converter.py](/examples/custom_converter.py)

Pre-made converters defined in [src/arc/converter/converters.py](/src/arc/converter/converters.py)