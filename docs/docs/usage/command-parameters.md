In *arc*, command-line parameters are defined using Python function arguments. *arc* has several kinds of parameters. Each corresponds with different input syntax and different declaration syntax.

## `arc.Argument`
`Argument` parameters are passed in positionally.

### Example
```py
--8<-- "examples/parameter_argument.py"
```

### Usage
```console
--8<-- "examples/outputs/parameter_argument"
```

### Notes
- If no default value is given, the argument is required.

### Arguments to `arc.Argument()`
- `name: str`: The name that will be used the the param on the command line
- `default: Any`: The default value for the param
- `description: str`: A string that documents the use / purpose of the parameter. Will be used in `--help` documentation
- `callback: Callable`: a function which will be called with the parsed value from the command line


## `arc.Option`
Options are (usually optional) parameters that are identified by keyword.

### Example

```py
--8<-- "examples/parameter_option.py"
```

### Usage
```console
--8<-- "examples/outputs/parameter_option"
```

### Notes
- Just like `Argument`, an `Option` is optional if the argument is given a default value, and required otherwise. However, it is usually good practice to make `Options` optional (hence the name).

### Arguments to `arc.Option()`
- `name: str`: The name that will be used the the param on the command line
- `short: str`: A length-one string that will be used for the short-name of this option (`--help -> -h`)
- `default: Any`: The default value for the param
- `description: str`: A string that documents the use / purpose of the parameter. Will be used in `--help` documentation
- `callback: Callable`: a function which will be called with the parsed value from the command line



## `arc.Flag`
Flags are similar to `Option` parameters as they are referenced by name, but they can only represent a boolean value (True / False) and do not recieve an associated value.

### Example
```py
--8<-- "examples/parameter_flag.py"
```
### Usage
```console
--8<-- "examples/outputs/parameter_flag"
```

### Notes
- Because flags can *only* represent two possible values, They are always optional. Absence of the flag implies False; presence of the flag implies True. That can be reversed by giving the argument a default of `True`.

### Arguments to `arc.Flag()`
- `name: str`: The name that will be used the the param on the command line
- `short: str`: A length-one string that will be used for the short-name of this option (`--help -> -h`)
- `default: bool`: The default value for the param. Defaults to `False`
- `description: str`: A string that documents the use / purpose of the parameter. Will be used in `--help` documentation
- `callback: Callable`: a function which will be called with the parsed value from the command line


## `arc.Count`
`Count` is a special kind of flag that instead of representing a boolean values, counts how many times it is referred to.
### Example
```py
--8<-- "examples/parameter_count.py"
```
### Usage
```console
--8<-- "examples/outputs/parameter_count"
```
### Arguments to `arc.Count()`
- `name: str`: The name that will be used the the param on the command line
- `short: str`: A length-one string that will be used for the short-name of this option (`--help -> -h`)
- `default: int`: Default value if the param is not present in the input. Defaults to `0`.
- `description: str`: A string that documents the use / purpose of the parameter. Will be used in `--help` documentation
- `callback: Callable`: a function which will be called with the parsed value from the command line


## Parameter Shorthand
If you've read any other arc documentation, you may have noticed them use parameters without using `Argument`, `Option`, and `Flag`. For convenience, arc allows a shorthand for parameters. For example, we can simplify this command:
```py
import arc

@arc.command()
def hello(
    firstname = arc.Argument(),
    lastname = arc.Option(default=""),
    reverse = arc.Flag()
):
    ...
```

To:
```py
import arc

@arc.command()
def hello(firstname, *, lastname="", reverse: bool):
    ...
```
Now, let's break this down by parameter.

`firstname`

Python considers `firstname` a "positional or keyword" parameter; in arc, this means it is a positional `Argument`. For implementation reasons, [positional-only arguments](https://www.python.org/dev/peps/pep-0570/) are not allowed.

`lastname`

In Python, any argument that comes after a bare `*` is a [keyword-only argument](https://www.python.org/dev/peps/pep-3102/). Since `Options` are analogous to keyword-only arguments, arc uses these same semantics. Because `lastname` comes after the bare `*`, is is an `Option`.

`reverse`
Finally, annotating `reverse` as `bool` makes it a `Flag` because flags represent boolean values. While `bool` has a special meaning in arc it isn't the only valid annotaion. Refer to [the section below](#type-annotations) for more info.

???+ Note
    The shorthand is only useful for very simple params. Any additional features (documentation, short names, callbacks, etc..) still make use of `Argument / Option / Flag`. Additionally,
    there is no shorthand for `Count` so it must be explictly specified every time.
???+ Tip
    Classful syntax only supports `Flag` shorthand using the `bool` type annotation.

## Type Annotations
*arc* uses argument type hints for data validation / conversion. For example, say we want to write a command that can sum two numbers together:
```py
from arc import CLI

cli = CLI()

@cli.command()
def add(val1: int, val2: int):
    print(f"The answer is: {val1 + val2}")

cli()
```
```
$ python example.py add 5 10
The answer is: 15
```
if the input fails to validate, arc will report a user-friendly error for the type
```
$ python example.py add 5 not-a-number
Invalid value for val2: not-a-number is not a valid integer
```

Some note about types:

- if a parameter does not specify a type, arc implicitly types it as `str`.
- Reference [Parameter Types](parameter-types.md) for a comprehensive list of all supported types.


## Parameter Sources
While generally, input is parsed from the command line, there are a few other sources that can be used to provide input.

The precedence of sources is:

1. Commane Line
2. Environment Variables
3. Input Prompt
4. Default Value

### Environment Variables
```py title="examples/from_env.py"
--8<-- "examples/from_env.py"
```
Now, if the argument isn't present ont he command line, it will be parsed from the environment `VAL`
```console
--8<-- "examples/outputs/from_env"
```
### Input Prompt
If there is no input provided on the command line for `name`, *arc* will prompt the user for input.
```py title="examples/from_prompt.py"
--8<-- "examples/from_prompt.py"
```
```console
$ python from_prompt.py Jolyne
Hello, Jolyne

$ python from_prompt.py
What is your name? Jolyne
Hello, Jolyne
```
If the parameter is optional, the user will be still be prompted, but the user can enter an empty input by just pressing *Enter* and the default will be used.