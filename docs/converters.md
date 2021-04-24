# Type Converters
- [Type Converters](#type-converters)
  - [Builtin Converters](#builtin-converters)
  - [Future Converters](#future-converters)
  - [Custom Converters](#custom-converters)




## Builtin Converters
| Indicator | Class Name      | Converts               | Conversion Method                                    | Other Notes                                          |
| --------- | --------------- | ---------------------- | ---------------------------------------------------- | ---------------------------------------------------- |
| str       | StringConverter | name=Jonathen          | python builtin `str()`                               |
| byte      | ByteConverter   | name=Terry             | python builtin `str.encode()`                        |
| int       | IntConverter    | number=4               | python builtin `int()`                               |
| float     | FloatConverter  | number=3.5             | python builtin `float()`                             |
| list      | ListConverter   | my_list=1,2,3,4,5      | Splits on commas, strips spaces                      | Use the generic List[\<type\>] for nested conversion |
| File      | FileConverter   | filename=/path/to/file | Creates a file handeler object                       | Specify file mode: File[File.<WRITE, READ, APPEND>]  |
| Enum      | EnumConverter   | mode=1,2,3             | Checks the value against possible values in the Enum |

## Future Converters
| Indicator | Class Name    | Converts                    | Conversion Method |
| --------- | ------------- | --------------------------- | ----------------- |
| dict      | DictConverter | my_dict=key:value,key:value | ?                 |


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
from arc import config

config.add_converter(CircleConverter)
```

See a full example in [examples/custom_converter.py](/examples/custom_converter.py)

Pre-made converters defined in [src/arc/converter/converters.py](/src/arc/converter/converters.py)

