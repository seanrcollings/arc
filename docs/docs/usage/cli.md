`#!python @arc.command()` can be used to create applications with multiple parameters like `echo` or `grep`.

`#!python arc.CLI()` is used to create a cli-tool with multiple commands where each can have their own parameters, like `git`


## Example
```py title="cli_demo.py"
--8<-- "examples/cli_demo.py"
```
We can check out the usage for the cli with `--help`. Then execute the commands by referencing them by name.
```console
--8<-- "examples/outputs/cli_demo"
```

???+ tip "Command Specific Help Documentation"
    Not only does the entire application have a `--help` flag, each command
    has a specialized `--help`
    ```console
    --8<-- "examples/outputs/cli_demo_help"
    ```

## Subcommands
`#!python arc.CLI()` also enables arbitrary nesting of commands. When you create a command with `#!python @cli.command()`, subcommands can be added to it with `#!python @command.subcommand()`

```py title="cli_subcommands.py"
--8<-- "examples/cli_subcommands.py"
```
Subcommands are executed by prefixing the command name with all of it's parent's names, all the way up to the root, with each name seperated by colons (`grandparent:parent:command`)
```console
--8<-- "examples/outputs/cli_subcommands"
```

Some notes about subcommands:

- Subcommands inherit their parent's [state](command-state.md).
- Subcommand will inherit their parent's [callbacks](callbacks.md).

## Multiple Files
`#!python arc.CLI()` makes it easy to break you application out into multiple files.


There are two ways to create a stand-alone command:

### `#!python @arc.command()`

We've been using `#!python @arc.command()` to create single-command applications, but any command created with `#!python @arc.command()` may also be used with `#!python arc.CLI()`.

### `#!python arc.namespace()`

`#!python arc.namespace()` is a special function that is used to create a namespace for subcommands. When executing the namespace directly, it will simply print out it's own help information.

The following is an example of how to (mostly) emulate what namespace does.

```py title="namespace_example.py"
--8<-- "examples/namespace_example.py"
```
```console
--8<-- "examples/outputs/namespace_example"
```

### Putting it Together

=== "cli_main.py"
    ```py
    --8<-- "examples/cli_main.py"
    ```
=== "cli_command.py"
    ```py
    --8<-- "examples/cli_command.py"
    ```

=== "cli_namespace.py"
    ```py
    --8<-- "examples/cli_namespace.py"
    ```

```console
--8<-- "examples/outputs/cli_main"
```


## Global Options
TODO