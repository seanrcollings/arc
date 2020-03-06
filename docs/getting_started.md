# Getting Started

- [Getting Started](#getting-started)
- [Creating a CLI](#creating-a-cli)
  - [Creating a Command](#creating-a-command)
  - [Running the CLI](#running-the-cli)
  - [Putting it together](#putting-it-together)
  - [Help Command](#help-command)
  - [Command Options & Flags](#command-options--flags)


# Creating a CLI
At it's simplest, Arc centers around a CLI object
```py
from arc import CLI

cli = CLI()
```

## Creating a Command
Commands are created using Python decorators. A function becomes a command using the `cli.script()` decorator. You must past at least a name into the script decorator. This will be the name used to execute the command.

```py
@cli.script("hello")
def hello():
    print("Hello, World!")
```

## Running the CLI
To run the CLI, you simply need to call the cli, like you would call a regular function
```py
cli()
```
The call does not accept any paramters, and should ideally be placed at the end of your file.

## Putting it together
```py
from arc import CLI

cli = CLI()

@cli.script("hello")
def hello():
    '''Command that prints Hello World'''
    print("Hello, World!")

cli()
```

```
$ python example.py hello
Hello, World!
```


## Help Command
All CLI's come bundled with a help command that displays all installed commands. The command uses the function's docstring as it's documentation
```
$ python example.py help
Usage: python3 FILENAME [COMMAND] [ARGUEMENTS ...]

Possible Options:
help
    Helper List function
        Prints out the docstrings for the clis's scripts

hello
    Command that prints Hello World
```

If you want a more specific help command, simpley over ride the builtin one with a script of your own
```py
@cli.script("help")
def helper():
    # print out your helper :)
```


## Command Options & Flags
Check this [doc](./options_and_flags.md) for info on options and flags

