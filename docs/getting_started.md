# Getting Started

- [Getting Started](#getting-started)
- [Creating a CLI](#creating-a-cli)
  - [Creating a Command](#creating-a-command)
  - [Running the CLI](#running-the-cli)
  - [Putting it together](#putting-it-together)
  - [Help Command](#help-command)
  - [Arc Features](#arc-features)


# Creating a CLI
At it's simplest, Arc centers around a CLI object
```py 1
from arc import CLI

cli = CLI()
```

## Creating a Command
Commands are created using Python decorators. A function becomes a command using the `cli.comand()` decorator. You can pass a name into the command decorator. If there isn't an explicit name, the function's name will be used This will be the name used to execute the command.

```py 2
@cli.command("hello")
def hello():
    print("Hello, World!")
```

## Running the CLI
To run the CLI, you simply need to call the cli, like you would call a regular function
```py 3
cli()
```


## Putting it together
```py
from arc import CLI

cli = CLI()

@cli.command("hello")
def hello():
    '''Command that prints Hello World'''
    print("Hello, World!")

cli()
```

```out
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

If you want a more specific help command, simpley over ride the builtin one with a command of your own
```py
@cli.comand("help")
def helper():
    # print out your helper :)
```


## Arc Features
- [Commands](./commands.md)
- [Options and Flags](./options_and_flags.md)
- [Converters](./converters.md)
- [Command Types](./scripts/scripts.md)

