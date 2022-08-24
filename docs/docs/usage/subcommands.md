In all of the examples so far, we've had a single command, with a single set of parameters. This works fine for smaller applications, but once a tool starts to grow in scope, it is useful to start breaking up it's functionality into descrete units using **subcommands**.

## What is a Subcommand?
A **subcommand** is an *arc* command object that lives underneath another command object. Each subcommand will have it's own callback function and it's own set of parameters. When ran from the commandline it will look a little something like this

```console
$ python example.py <global-options> <subcommand> <options>
```

### Example
There are a couple of ways to define subcommands, in this doc we'll focus on the most common

```py title="examples/subcommand.py"
--8<-- "examples/subcommand.py"
```

We can then execute each subcommand by referring to them by name.
```console
--8<-- "examples/outputs/subcommand"
```


### Documentation
Subcommands also get their own `--help`
```console
--8<-- "examples/outputs/subcommand_help"
```
They're all pretty bare-bones right now, but they will fill out as the application grows.

### Nesting Subcommands
Subcommands can be arbitrarly nested
```py title="examples/nested_subcommands.py"
--8<-- "examples/nested_subcommands.py"
```

```console
--8<-- "examples/outputs/nested_subcommands"
```

## Global Parameters
When you define subcommands for you application, the root `#!python @arc.command()` object becomes a callback for *global* parameters. This is useful for defining things that can apply to the entirety of your applcation. For example, logging configuration.

```py title="examples/global_params.py"
--8<-- "examples/global_params.py"
```

```console
--8<-- "examples/outputs/global_params"
```

Global arguments **must** come before the name of the command for them to be interpreted correctly. You can see this reflected in the `--help`

```console
--8<-- "examples/outputs/global_params_help"
```

### Things to be aware of
- The root object can no longer define [argument parameters](parameters/arguments.md), because *arc* doesn't have a way of knowing *what* is a positional parameter and *what* is the name of a command. **Note**: This may change in the future if I have time / care to change it.
- The root callback will be executed before *every* subcommand, regardless of whether or not you actually provide any global arguments. If this behavior isn't desired, it can be changed with `#!python arc.configure(global_callback_execution="args_present")`

## Naming Subcommands
By default, commands are the kebab-case version of the function they decorate. This can be modified to change the name

```py
import arc

@arc.command()
def command():
    ...

@command.subcommand("some-other-name")
def sub():
    ...

command()
```

or provide *multiple* names, for a command.
```py
import arc

@arc.command()
def command():
    ...

@command.subcommand(("some-other-name", "another-name", "a-third-name"))
def sub():
    ...

command()
```
## Subcommands in other Files
Breaking up your CLI interface into multiple files in *arc* is a very straightforward process.

=== "subcommand.py"

    ``` py
    import arc

    @arc.command()
    def sub():
        print("This is the subcommand")

    # Notice, no call to sub()
    ```

=== "cli.py"

    ``` py
    import arc
    from subcommand import sub


    @arc.command()
    def cli():
        print('hello there!')

    # Here we add sub as a subcommand to cli
    cli.add_command(sub)

    cli()
    ```

