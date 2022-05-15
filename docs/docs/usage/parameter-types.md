When Possible, *arc* uses builtin and standard library data types for arguments. But if no type is available, or the builtin types don't provide the neccessary functionality, *arc* may implement a custom type.

## Standard Libary Types

`#!python str`

This is considered the default type is no type is specified. `#!python str(v)` is used which, in most cases, will be comparable to no change

`#!python int`

arc uses `#!python int(v)` to convert the value. Note that decimal input (`1.4`) will result in an error, not a narrowing operation.

`#!python float`

Likewise, arc uses `#!python float(v)`. Ingeter values will be converted to a float (`2 -> 2.0`)

`#!python bool`

Used to denote a `Flag`

`#!python bytes`

Converted using `#!python v.encode()`

### Collection Types

`#!python list`

Collection types (`#!python list`, `#!python set`, `#!python tuple`) can be used to gather multiple values into a single parameter.
When used as a positional parameter `#!python list` acts similarly to `#!python *args`
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

`#!python set`

Similar to `list`, but will filter out any non-unique elements.

```py title="set_argument.py"
--8<-- "examples/set_argument.py"
```
```console
--8<-- "examples/outputs/set_argument"
```

`#!python tuple`

Similar to `list`, but with some additional functionality.

According to PEP 484:

- `#!python tuple` represents an arbitrarily sized tuple of any type. In *arc*, this will behave the same as `#!python list`
- `#!python tuple[int, ...]` represents an arbitrarily sized tuple of integers. In *arc*, this will behave the same as `#!python list[int]`
- `#!python tuple[int, int]` represents a size-two tuple of integers. In *arc*, this behavior is unique to `#!python tuple` as the parameter will only select 2 values from input.

`#!python dict`

Allows a list of comma-seperated key-value pairs. Can be typed generically on both keys and values.
```py title="dict_argument.py"
--8<-- "examples/dict_argument.py"
```
```console
--8<-- "examples/outputs/dict_argument"
```


`#!python typing.Union`

Allows the input to be multiple different types.
```py title="union_argument.py"
--8<-- "examples/union_argument.py"
```
```console
--8<-- "examples/outputs/union_argument"
```

arc will attempt to coerce the input into each type, from left to right. The first to succeed will be passed along to the command.

!!! warning
    Currently *arc's* behavior with collections in union types is not defined. As such, it is not reccomended that you give an argument a type similar to `#!python typing.Union[list, ...]`

`#!python typing.Literal`

Enforces that the input must be a specific sub-set of values
```py title="literal_argument.py"
--8<-- "examples/literal_argument.py"
```
```console
--8<-- "examples/outputs/literal_argument"
```
!!! note
    *arc* compares the input to the string-ified version of each value in the Literal. So for the second example above, the comparison that succedded was `"1" == "1"` not `1 == 1`.

`#!python typing.TypedDict`

Constrains a dictionary input to a specific subset of keys and specific value types.

`#!python typing.Optional`

Indicates an optional parameter with a default of `None`. The following are functionality equivalent
```py title="optional_argument.py"
--8<-- "examples/optional_argument.py"
```
```console
--8<-- "examples/outputs/optional_argument"
```


`#!python pathlib.Path`

Path won't perform any validation checks to assert that the input is a valid path, but it just offers the convenience of working with path objects rather than strings. Check the `ValidPath` custom type for additional validations

`#!python enum.Enum`

Similar to `#!python typing.Literal`, restricts the input to a specific sub-set of values
```py title="paint.py"
--8<-- "examples/paint.py"
```
```console
--8<-- "examples/outputs/paint"
```

`#!python ipaddress.IPv4Address`

Uses `#!python ipaddress.IPv4Address(v)` for conversion, so anything valid there is valid here.

`#!python ipaddress.IPv6Address`

Same as above

## Arc Types
*arc* provides a variety of additional types exported from the `#!python arc.types` module:

???+ warning
    Most custom *arc* types are usable as a valid *arc* parameter type and as a typical Python class. For example, you can create a `SemVar` object easily like so: `#!python SemVer.parse('1.2.3')`. In some particular instances, a type can *only* be used as a argument type and not as a valid constructor. These types will be denoted with `🛇` following the type name.

`Context`

Gives you access to the current execution context instance which serves as a central data and functionality object


`State`

Reference [State](./command-state.md) for details


`Range`

TODO


`SemVer`

TODO

`User` (**UNIX ONLY**)

A representation of a unix user.

`Group` (**UNIX ONLY**)

A representation of a unix group.

### File System Types


`File`

TODO

`ValidPath`

Subclass of `#!python pathlib.Path` but asserts that the provided path actually exists


`FilePath`

Subclass of `ValidPath` but asserts that the path both exists and is a file


`DirectoryPath`

Subclass of `ValidPath` but assets that the path both exists and is a directory

### Networking Types

`IpAddress` 🛇

Can be either `IPv4Address` or `IPv6Address`. Equivelant to `#!python typing.Union[IPv4Address, IPv6Address]`

`Url`

Parses the strings input using `#!python urllib.parse.urlparse`

`HttpUrl`

`Url` that asserts the scheme to be `http` or `https`

`PostgresUrl`

`Url` that asserts the scheme to be `postgresql` or `postgres`

### Number Types
???+ note
    For any types that simply change the base of the input (like `Binary` or `Hex`), it is essentially equivelant to `int(v, base=<base>)`.

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
When implementing your own types, you can make them compatible with arc by implementing the `#!python __convert__()` class method. Arc will call this with the input from the command line, and you are expected to parse the input and return an instance of the type.

```py title="custom_type.py"
--8<-- "examples/custom_type.py"
```
```console
--8<-- "examples/outputs/custom_type"
```

Some notes about custom types:

- In additon to `value`, you can also add the following arguments to the signature (in the given order, but the names don't need to match):
  - `info`: Description of the provided type. Instance of `#!python arc.types.TypeInfo`
  - `ctx`: The current execution context. Instance of `#!python arc.context.Context`

???+ tip
    Any type that implements `#!python __enter__() ` and `#!python __exit__()`, will be treated like a context manager. The manager will be opened before the command executes, and closed afterwards.

### Type Aliases
Type aliases are the way in which *arc* implements support for builtin and standard library Python types, but can also be used for any type. You can use type aliases to provide support fo any third party library types. For example, supporting numpy arrays
```py
import arc
from arc.types import Alias
import numpy as np

# Inherits from Alias. The 'of' parameter declares what types(s) this
# alias handles (can be a single type or tuple of types).
# Reads like a sentence: "NDArrayAlias is the Alias of np.ndarray"
class NDArrayAlias(Alias, of=np.ndarry):

    @classmethod
    def __convert__(cls, value: str):
        return np.ndarray(value.split(","))


@arc.command()
def main(array: np.ndarray):
    print(repr(array))


main()
```
```console
$ python example.py x,y,z
array(['x', 'y', 'z'], dtype='<U1')
```
All other principles about custom types hold for alias types.

Note that this is a simplified example, a more complete implementation would support the use of generics using `#!python numpy.typing`
### Generic Types
TODO














