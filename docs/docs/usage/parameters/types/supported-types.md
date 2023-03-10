This document outlines all of the types that *arc* supports for parameters.

When possible, *arc* uses builtin and standard library data types. But if no type is available, or the builtin types don't provide the neccessary functionality, *arc* may implement a custom type.

## Standard Library Types

`#!python str`, `#!python typing.Any`

`#!python str(v)` is used which, in most cases, will be comparable to no change.

This is considered the default type is no type is specified.

`#!python int`

*arc* uses `#!python int(v)` to convert the value. Note that decimal input (`1.4`) will result in an error, not a narrowing operation.

`#!python float`

Likewise, *arc* uses `#!python float(v)`. Ingeter values will be converted to a float (`2 -> 2.0`)

`#!python bool`

Used to denote a [`Flag`](../flags.md)

```py title="examples/parameter_flag.py"
--8<-- "examples/parameter_flag.py"
```

```console
--8<-- "examples/outputs/parameter_flag"
```

`#!python bytes`

Converted using `#!python v.encode()`

`#!python dict`

Allows a list of comma-seperated key-value pairs. Can be typed generically on both keys and values.
```py title="dict_argument.py"
--8<-- "examples/dict_argument.py"
```
```console
--8<-- "examples/outputs/dict_argument"
```

`#!python typing.TypedDict`

Constrains a dictionary input to a specific subset of keys and specific value types.

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
    You cannot have a type like `#!python typing.Union[list, int]` as collection types need to be known at definition of a command rather
    than during data validation.

Python 3.10's union syntax is also valid: `int | str`


`#!python pathlib.Path`

Path won't perform any validation checks to assert that the input is a valid path, but it just offers the convenience of working with path objects rather than strings. Check the `ValidPath` custom type for additional validations

`#!python ipaddress.IPv4Address`

Uses `#!python ipaddress.IPv4Address(v)` for conversion, so anything valid there is valid here.

`#!python ipaddress.IPv6Address`

Same as above


`#!python re.Pattern`

Compile a regular expression using `#!python re.compile()`

### Collection Types

*arc* allows you to collect *multiple* values from the command line into a single argument for your comamnd. To do this, you use the collection types: `#!python list`, `#!python set` and `#!python tuple`

`#!python list`

```py title="list_argument.py"
--8<-- "examples/list_argument.py"
```
```console
--8<-- "examples/outputs/list_argument"
```
Because `list` can accept any number of values, you won't be able to add additional arguments after `names`. Any other positional arguments would have to come before `names`.


`#!python set`

Similar to `#!python list`, but will filter out any non-unique elements.

```py title="set_argument.py"
--8<-- "examples/set_argument.py"
```
```console
--8<-- "examples/outputs/set_argument"
```

`#!python tuple`

Similar to `#!python list`, but with some additional functionality.

According to PEP 484:

- `#!python tuple` represents an arbitrarily sized tuple of any type. In *arc*, this will behave the same as `#!python list`
- `#!python tuple[int, ...]` represents an arbitrarily sized tuple of integers. In *arc*, this will behave the same as `#!python list[int]`
- `#!python tuple[int, int]` represents a size-two tuple of integers. In *arc*, this behavior is unique to `#!python tuple` as the parameter will only select 2 values from input.

#### Sub Typing
Collections can be sub-typed so that each item will be converted to the proper type:
```py title="sum.py"
--8<-- "examples/sum.py"
```
```console
--8<-- "examples/outputs/sum"
```

#### Collections as Options
When used as an option, it allows the option to be used multiple times:
```py title="list_option.py"
--8<-- "examples/list_option.py"
```
```console
--8<-- "examples/outputs/list_option"
```

#### Collection Lengths
You can specify how many items should be provided to a collection type with a [type validator](./type-middleware.md), specifically [`#!python Len()`](../../../reference/types/validators.md#Len)

```py title="examples/length.py"
--8<-- "examples/length.py"
```

```console
--8<-- "examples/outputs/length"
```

### Constrained Input

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

`#!python enum.Enum`

Similar to `#!python typing.Literal`, restricts the input to a specific sub-set of values
```py title="examples/paint.py"
--8<-- "examples/paint.py"
```
```console
--8<-- "examples/outputs/paint"
```

## *arc* Types
*arc* provides a variety of additional types exported from the `#!python arc.types` module:

???+ warning
    *arc* types are sort of weird in the general Python sense. While it will become
    more aparent later as to why this is the case, know that you cannot usually
    create the types on your own and have the expected behavior. If you do need / want
    to do this, you can use: `#!python arc.convert(<value>, <type>)`

`Context`

Gives you access to the current execution context.


`State`

Reference [State](../../command-state.md) for details

`Prompt`

Gives you access to a [Prompt instance](../../user-input.md)

`SemVer`

A type to support semantically-versioned strings based on the spec found [here](https://semver.org/spec/v2.0.0.html)

`User` (**UNIX ONLY**)

A representation of a unix user.

`Group` (**UNIX ONLY**)

A representation of a unix group.

### File System Types

`File`

One of the most common things that a CLI tool is likely to do, is take in a file name as input, and interact with that file in some way. *arc's* advanced typing system makes this trivial, with the details around ensuring the file exists, opening it, and closing it handled by *arc* for you.


*arc* provides this functionality through its [`#!python arc.types.File`](../../../reference/types/file.md) type. Let's use it to read out the first line of the source code's README.

```py title="examples/types/file.py"
--8<-- "examples/types/file.py"
```

```console
--8<-- "examples/outputs/types/file"
```

There are constants defined on `File` (like `File.Read` above) for all common actions (`Read`, `Write`, `Append`, `ReadWrite`, etc...). You can view them all in the [reference](../../../reference/types/file.md)


`ValidPath`

`#!python pathlib.Path` but asserts that the provided path actually exists


`FilePath`

`#!python pathlib.Path` but asserts that the path both exists and is a file


`DirectoryPath`

`#!python pathlib.Path` but asserts that the path both exists and is a directory

### Networking Types

`IpAddress`

Union type for `IPv4Address` and `IPv6Address`

`Url`

Parses the strings input using `#!python urllib.parse.urlparse`

`HttpUrl`

`Url` that asserts the scheme to be `http` or `https`

`WebSocketUrl`

`Url` that asserts the scheme to be `wss`

`FtpUrl`

`Url` that asserts the scheme to be `ftp`

`MysqlUrl`

`Url` that asserts the scheme to be `mysql

`PostgresUrl`

`Url` that checks that it is a valid PostgreSQL URL

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

`AnyNumber`

Accepts floats, and integers in any base.

### String Types

`Char`

Enforces that the string can only be a single character long

`Password`


When prompted for input, the user's input will not be echoed to the screen.






