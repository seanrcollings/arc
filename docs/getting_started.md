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
```py x
from arc import CLI

cli = CLI()
```

## Creating a Command
Commands are created using Python decorators. A function becomes a command using the `cli.script()` decorator. You can pass a name into the script decorator. If there isn't an explicit name, the function's name will be used This will be the name used to execute the command.

```py x
@cli.script("hello")
def hello():
    print("Hello, World!")
```

## Running the CLI
To run the CLI, you simply need to call the cli, like you would call a regular function
```py x
cli()
```


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

If you want a more specific help command, simpley over ride the builtin one with a script of your own
```py x 
@cli.script("help")
def helper():
    # print out your helper :)
```


## Arc Features
- [Options and Flags](./options_and_flags.md)
- [Converters](./converters.md)
- [Special Script Names](./special_script_names.md)
- [Utilities](./utilities.md)
- [Script Types](./scripts/scripts.md)

