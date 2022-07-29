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

### Root Command
When subcommands are added into the mix the root `#!python @arc.command()` object behaves a little bit differently.

TODO: expound on:

- Cannot have positional arguments
- It's arguments are considered global
- It will be executed for any subcommand that is executed

## Naming Subcommands

## Subcommands in other Files