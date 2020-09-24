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
```py 1
from arc import CLI

cli = CLI()
```

## Creating a Command
Commands are created using Python decorators. A function becomes a command using the `cli.script()` decorator. You can pass a name into the script decorator. If there isn't an explicit name, the function's name will be used This will be the name used to execute the command.

```py 2
@cli.script("hello")
def hello():
    print("Hello, World!")
```

## Running the CLI
To run the CLI, you simply need to call the cli, like you would call a regular function
```py 3
cli()
```

```out
$ python example.py hello
Hello, World!
```