In all of the examples so far, we've had a single command, with a single set of parameters. This works fine for smaller applications, but once a tool starts to grow in scope, it is useful to start breaking up it's functionality into descrete units using **subcommands**.

## What is a Subcommand?
A **subcommand** is an *arc* command object that lives underneath another command object. Each subcommand will have it's own callback function and it's own set of parameters. When ran from the commandline it will look a little something like this

```console
$ python example.py <subcommand> <options>
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

## Root Command
It is important to note that when using subcommands, the root command is still executable. One must take care that subcommand names may come into collision with arguments for the root or command (or any parent command, really). If you do not want a parent command to be executable, you may use this pattern:

```py title="examples/namespace.py"
--8<-- "examples/namespace.py"
```

```console
--8<-- "examples/outputs/namespace"
```

Namespace commands do not take any arguments (besides `--help`), and when invoked, will print out the usage for the command, and exit with an error code.

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

