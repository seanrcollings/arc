The simplest *arc* program would look like this
```py title="hello_world.py"
--8<-- "examples/hello_world.py"
```
Which we can then execute directly!
```console
--8<-- "examples/outputs/hello_world"
```

## Breakdown
Let's break this down to better understand what exactly is going on.

1. `#!python @arc.command()` is a Python decorator that transforms a function into an *arc* command.
2. `#!python def main()` is just a simple Python function. [The function can also declare parameters](command-parameters.md).
3. `#!python main()` while this make look like we're calling the `main` function, because the function has been transformed into a command, we're actualy executing the command.

## Multiple Commands
`#!python @arc.command()` is used to create a single *arc* command. To create a command-line tool with multiple commands, you will need to use `#!python arc.CLI`
```py title="cli_demo.py"
--8<-- "examples/cli_demo.py"
```
```
--8<-- "examples/outputs/cli_demo"
```
!!! tip
    `CLI` is a subclass of `Command`, so most things about one
    apply to the other