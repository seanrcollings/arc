*arc* uses [Python type hints](https://peps.python.org/pep-0484/) for data conversion / validation.

When Possible, *arc* uses builtin and standard library data types for arguments. But if no type is available, or the builtin types don't provide the neccessary functionality, *arc* may implement a custom type.

## Builtin Types

`#!python str`

This is considered the default type is no type is specified. `#!python str(v)` is used which, in most cases, will be comparable to no change

`#!python int`

arc uses `#!python int(v)` to convert the value. Note that decimal input (`1.4`) will result in an error, not a narrowing operation.

`#!python float`

Likewise, arc uses `#!python float(v)`. Ingeter values will be converted to a float (`2 -> 2.0`)

`#!python bool`

Used to denote a `Flag`

```py title="examples/parameter_flag.py"
--8<-- "examples/parameter_flag.py"
```

```console
--8<-- "examples/outputs/parameter_flag"
```

`#!python bytes`

Converted using `#!python v.encode()`

### Collection Types

Collection types are used by *arc* to collect **multiple values** into a single argument. Check the [next](multiple-values.md) page for information on how that works


## Standard Libary Types


`#!python typing.Union`

Allows the input to be multiple different types.
```py title="examples/union_argument.py"
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
```py title="examples/literal_argument.py"
--8<-- "examples/literal_argument.py"
```
```console
--8<-- "examples/outputs/literal_argument"
```
!!! note
    *arc* compares the input to the string-ified version of each value in the Literal. So for the second example above, the comparison that succedded was `"1" == "1"` not `1 == 1`.

`#!python typing.TypedDict`

Constrains a dictionary input to a specific subset of keys and specific value types.


`#!python pathlib.Path`

Path won't perform any validation checks to assert that the input is a valid path, but it just offers the convenience of working with path objects rather than strings. Check the `ValidPath` custom type for additional validations

`#!python enum.Enum`

Similar to `#!python typing.Literal`, restricts the input to a specific sub-set of values
```py title="examples/paint.py"
--8<-- "examples/paint.py"
```
```console
--8<-- "examples/outputs/paint"
```

`#!python ipaddress.IPv4Address`

Uses `#!python ipaddress.IPv4Address(v)` for conversion, so anything valid there is valid here.

`#!python ipaddress.IPv6Address`

Same as above


`#!python re.Pattern`

Support for regular expression patterns


## `arc` Types
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

`Password`








