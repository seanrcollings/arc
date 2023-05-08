This intro serves as a quick starting off point to see some of *arc's* most useful features.

## Hello World
The simplest *arc* program would look like this
```py title="hello_world.py"
--8<-- "examples/hello_world.py"
```
Which we can then execute directly!
```console
--8<-- "examples/outputs/hello_world"
```

Let's break this down to better understand what exactly is going on.

1. `#!python @arc.command` is a Python decorator that transforms a function into an *arc* command.
2. `#!python def main()` is just a simple Python function
3. `#!python main()` while this make look like we're calling the `main` function, because the function has been transformed into a command, we're actualy executing the command.

## Parameters
We can add parameters to the previous example by defining an argument. For example, instead of saying hello to the world, we can have the command say hello to a specific person that we can input:

```py title="examples/hello.py"
--8<-- "examples/hello.py"
```

```console
--8<-- "examples/outputs/hello"
```

## Documentation
Our argument and docstring get added automatcially to the `--help` output

```console
--8<-- "examples/outputs/hello_help"
```

## Type Hints
*arc* uses argument type hints for data validation / conversion. For example, say we want to write a command that can sum two numbers together:
```py title="examples/add.py"
--8<-- "examples/add.py"
```

```console
--8<-- "examples/outputs/add"
```
if the input fails to validate, *arc* will report a user-friendly error for the type
```console
--8<-- "examples/outputs/add_error"
```

Some note about types:

- if a parameter does not specify a type, *arc* implicitly types it as `#!python str`.
- **All** builtin types are supported by *arc*, and many stdlib types
- [Parameter Types](../parameters/types/supported-types) contains a comprehensive list of all supported types.

## Configuration
*arc* is easily configurable via the `#!python arc.configure()` function.

For example, you can set a version string for you application. This will add a `--version` flag to your application.

```py title="examples/hello_configuration.py"
--8<-- "examples/hello_configuration.py"
```

```console
--8<-- "examples/outputs/hello_configuration"
```


*View the [reference](../reference/config.md#arc.config.configure) for details on all the configuration options*
