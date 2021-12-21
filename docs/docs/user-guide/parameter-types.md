When Possible, *arc* uses builtin and standard library data types for arguments. But if no type is available, or the builtin types don't provide the neccessary functionality, *arc* may implement a custom type.

## Standard Libary Types

`str`

This is considered the default type is no type is specified. `str(v)` is used which, in most cases, will be comparable to no change

`int`

arc uses `int(v)` to convert the value. Note that decimal input (`1.4`) will result in an error, not a narrowing operation.

`float`

Likewise, arc uses `float(v)`. Ingeter values will be converted to a float (`2 -> 2.0`)

`bool`

Used to denote a `Flag`

`bytes`

Converted using `v.encode()`

### Collection Types

`list`

Collection types (`list`, `set`, `tuple`) can be used to gather multiple values into a single parameter.
When used as a positional parameter `list` acts similarly to `*args`
```py title="list_argument.py"
--8<-- "examples/list_argument.py"
```
```console
--8<-- "examples/outputs/list_argument"
```
Because `list` can accept any number of values, you won't be able to add additional arguments after `names`. Any other positional arguments would have to come before `names`.

When used as an option, it allows the option to be used multiple times:
```py title="list_option.py"
--8<-- "examples/list_option.py"
```
```console
--8<-- "examples/outputs/list_option"
```
Collections can be sub-typed so that each item will be converted to the proper type:
```py title="sum.py"
--8<-- "examples/sum.py"
```
```console
--8<-- "examples/outputs/sum"
```


`set`

Similar to `list`, but will filter out any non-unique elements.

```py
import arc

@arc.command()
def main(vals: set):
    print("Unique values:")
    print("\n".join(vals))

main()
```
```
$ python example.py 1 1 1 2 2 2 3 3 3 4 5
Unique values:
1
2
3
4
5
```


`tuple`

Similar to `list`, but with some additional functionality.

According to PEP 484:
- `tuple` represents an arbitrarily sized tuple of any type. This will functionally the same as `list`
- `tuple[int, ...]` represents an arbitrarily sized tuple of integers. This will be functionality the same as `list[int]`
- `tuple[int, int]` represents a size-two tuple of integers.



`dict`

Allows a list of comma-seperated key-value pairs. Can be typed generically on both keys and values.
```py
from arc import CLI
cli = CLI()

@cli.subcommand()
def dict_type(numbers: dict[str, int]):
    print(type(numbers))
    print(numbers)

cli()
```
```
$ python example.py dict-type one=1,two=2,three=3
<class 'dict'>
{'one': 1, 'two': 2, 'three': 3}
```


`typing.Union`

Allows the input to be multiple different types.
```py
from typing import Union
from arc import CLI
cli = CLI()

@cli.subcommand()
def union_type(number: Union[int, str]):
    print(type(number))

cli()
```

```
$ python example.py union-type 5
<class 'int'>

$ python example.py union-type somestring
<class 'str'>
```
arc will attempt to coerce the input into each type, from left to right. The first to succeed will be passed along to the command.


`typing.Literal`

Enforces that the input must be a specific sub-set of values
```py
from typing import Literal
from arc import CLI
cli = CLI()

@cli.subcommand()
def literal_type(word: Literal['foo', 'bar', 1]):
    print(value, type(value))

cli()
```
```
$ python example.py literal-type foo
foo <class 'str'>


$ python example.py literal-type 1
1 <class 'int'>

$ python example.py literal-type other
Invalid value for word: ainfeianf must be foo, bar or baz
```
> **Note**: Arc compares the input to the string-ified version of each value in the Literal. So for the second example above, the comparison that succedded was `"1" == "1"` not `1 == 1`.


`typing.TypedDict`

Constrains a dictionary input to a specific subset of keys and specific value types.


`pathlib.Path`

Path won't perform any validation checks to assert that the input is a valid path, but it just offers the convenience of working with path objects rather than strings. Check the `ValidPath` custom type for additional validations

`enum.Enum`

Similar to `typing.Literal`, restricts the input to a specific sub-set of values
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
        print("You painted the walls the bloodiest of reds")
    elif color == Color.YELLOW:
        print("You painted the walls the most fabulous yellow")
    else:
        print("You painted the walls the deepest of greens")

cli()
```
Since red is a defined value on the `Color` enumeration, it is a valid argument value
```
$ python example.py paint red
You painted the walls the bloodiest of reds
```
Any other value will be considered invalid
```
$ python example.py paint blue
ERROR: Argument color must be one of: red, yellow, or green, but was blue.
```

`ipaddress.IPv4Address`

Uses `ipaddress.IPv4Address(v)` for conversion, so anything valid there is valid here.

`ipaddress.IPv6Address`

Same as above

## *arc* Types
*arc* provides a variety of additional types exported from the `arc.types` module:

???+ warning
    Most custom *arc* types are usable as a valid *arc* paramater type and as a typical Python class. For example, you can create a `SemVar` object easily like so: `SemVer.parse('1.2.3')`. In some particular instances, a type can *only* be used as a argument type and not as a valid constructor. These types will be denoted with `🛇` following the type name.

`Context`

Gives you access to the current execution context instance which serves as a central data and functionality object


`State`

Reference [State](./command-state.md) for details


`Range`

TODO


`SemVer`

TODO

### File System Types


`File`

TODO

`ValidPath`

Subclass of `pathlib.Path` but asserts that the provided path actually exists


`FilePath`

Subclass of `ValidPath` but asserts that the path both exists and is a file


`DirectoryPath`

Subclass of `ValidPath` but assets that the path both exists and is a directory

### Networking Types

`IpAddress` 🛇

Can be either `IPv4Address` or `IPv6Address`. Equivelant to `typing.Union[IPv4Address, IPv6Address]`

`Url`

Parses the strings input using `urllib.parse.urlparse`

`HttpUrl`

`Url` that asserts the scheme to be `http` or `https`

`PostgresUrl`

`Url` that asserts the scheme to be `postgresql` or `postgres`

### Number Types
> Note for any types that simply change the base of the input (like `Binary` or `Hex`), it is essentially equivelant to `int(v, base=<base>)`.

`Binary`

Accepts integers as binary stings (`0101010110`).

`Oct`

Accepts integers in base 8

`Hex`

Accepts integers in base 16

`PositveInt`

Enforces that the integer must be greater than 0

`NegativeInt`

Enforces that the integer must be less than 0

`PositveFloat`

Enforces that the float must be greater than 0

`NegativeFloat`

Enforces that the float must be less than 0

`AnyNumber` 🛇

Accepts floats, and integers in any base.

### String Types

`Char`

Enforces that the string can only be a single character long

### Strict Types

`strictstr`


`strictint`


`strictfloat`


`stricturl`


`strictpath`


## Custom Types
When implementing your own types, you can make them compatible with arc by implementing the `__convert__()` class method. Arc will call this with the input from the command line, and you are expected to parse the input and return an instance of the type.

```py
from arc import CLI, errors

cli = CLI()


class CustomType:
    def __init__(self, val: int):
        self.val = val

    def __str__(self):
        return f"CustomType(val={self.val})"

    @classmethod
    def __convert__(cls, value: str):
        if value.isnumeric():
            return cls(int(value))
        else:
            raise errors.ConversionError(value, "must be an integer")

@cli.command()
def command(foo: CustomType):
    print(foo)

cli()
```
Some notes about custom types:
- In additon to `value`, you can also add the following arguments to the signature (in the given order, but the names don't need to match):
  - `info`: Description of the provided type. Instance of `arc.types.TypeInfo`
  - `ctx`: The current execution context. Instance of `arc.context.Context`

- Any type that implements the `__exit__()` method will be treated as a context manager resouces and will be closed using that `__exit__()` method after the command completes it's execution.

```
$ python example.py command 2
CustomType(val=2)
$ python example.py command not-a-number
Invalid value for foo: must be an integer
```

### Type Aliases
Type aliases are the way in which arc implements support for builtin and standard lib Python types, but can also be used for any type. You can use type aliases to provide support fo any third party library types. For example, supporting numpy arrays
```py
from arc import CLI
from arc.types import Alias
# Requires numpy to be installed
import numpy as np

# Inherits from Alias. The 'of' parameter declares what types(s) this
# alias handles (can be a single type or tuple of types).
# Reads like a sentence: "NDArray is the Alias of np.ndarray"
class NDArray(Alias, of=np.ndarry):

    @classmethod
    def __convert__(cls, value: str):
        return np.array(value.split(","))


cli = CLI()


@cli.command()
def command(array: np.ndarray):
    print(repr(array))


cli()
```
```
$ python example.py command x,y,z
array(['x', 'y', 'z'], dtype='<U1')
```
All other principles about custom types hold for alias types.

Note that this is a simplified example, a more complete implementation would support the use of generics using `numpy.typing`
### Generic Types
TODO














