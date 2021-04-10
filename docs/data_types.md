# Data Types

## Use
Typically, you don't want numbers, booleans, lists, represented as just strings. Arc provides type conversions that will convert the input to your desired type before passing it on to the command. If you've used Flask before, it's URL converters work in essentially the same way. If no type is specified, the input will be left as a string


## Examples
### Int Conversion
```py
from arc import CLI

cli = CLI()

@cli.subcommand()
def number_type(number: int):
    '''Prints the type of a number'''
    print(type(number))

cli()
```

```out
$ python3 example.py number_type number=5
<class 'int'>
```

### Float Converion
```py
from arc import CLI
cli = CLI()

@cli.subcommand()
def float_type(number: float):
    '''Prints the type of a float'''
    print(type(number))

cli()
```

```out
$ python3 example.py float_type number=5.3
<class 'float'>
```
Check [examples/converters.py](/examples/converters.py) for full examples of builtin types


## Enum Type
You can use the Python standard library Enum to define a specific subset of acceptable values to an argument.
```py
from enum import Enum
from arc import CLI

cli = CLI()

class Color(Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"

@cli.command()
def paint(color: Color):
    if color == Color.RED:
        print("You painted the walls the bloodiest reds")
    elif color == Color.YELLOW:
        print("You painted the walls the most fabulous yellow")
    else:
        print("You painted the walls the deepest of blues")

cli()
```

We can then run:
```out
$ python3 example.py paint color=red
You painted the walls the bloodiest of reds
```
Since red is a defined value on the `Color` enumeration.

## File Type
A file type will take in a file path and return a file handler object
```py x
from arc import CLI
from arc.types import File
cli = CLI()

@cli.command()
def file_test(file=File[File.READ]):
    # file will be of custom type File, but has the same interface as the TextIOWrapper returned by open()
    print(file.readlines())
```
The format for a File types is File[<FILE_MODE>] with the available file modes being:
  - READ
  - WRITE
  - APPEND
  - CREATE

Arc should handle the file cleanup process, however if you want to control when the file closes, you can with `file.close()`. Additionally, the file object implements `__enter__` and `__exit__` so can be used as a context manager.
```py
from arc import CLI
from arc.types import File
cli = CLI()

@cli.command()
def file_test(file=File[File.READ]):
    print(file.readlines())
    file.close()

    # OR

    with file as f:
        print(f.readlines())

    # With either approach, file will defintely be closed at this point

# unless something goes horribly wrong, once the function finishes execution ARC will close the file for you though.
```





## Input Data Type Converter Functions
Arc also allows you to use it's converter functionality when gathering user input from within a command
```py
from arc import CLI
from arc.convert.input import convert_to_int

cli = CLI()

@cli.subcommand("example")
def example():
  cool_number = convert_to_int("Please enter a number: ")
  print(type(cool_number)) # '<class : int>'

cli()
```
Note that all convereters in `Config.converter` will have a function associated with it. This includes all custom converters. The functions will be named `convert_to_<indicator>`

Note that if the command defines a custom converter, it's respective input function will need to be imported after it is added to `Config.converter` otherwise it doesn't yet exist to import.