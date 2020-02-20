# Getting Started

## Quick example



## Creating a CLI
```py
from cli import CLI

cli = CLI()
```

## Creating a Command
Commands are created using Python decorators. A function becomes a command using the `cli.script()` decorator. You must past at least a name into the script decorator. This will be name used to execute the command.

```py
@cli.script("hello")
def hello():
    print("Hello, World!")

```

## Running the CLI
To run the CLI

## Putting it together
```py
from cli import CLI

cli = CLI()

@cli.script("hello")
def hello():
    print("Hello, World!")

cli()
```

```
$ python example.py hello
Hello, World!
```