# Getting Started

- [Getting Started](#getting-started)
- [Creating a CLI](#creating-a-cli)
  - [Creating a Command](#creating-a-command)
  - [Running the CLI](#running-the-cli)
  - [Putting it together](#putting-it-together)
  - [Help Command](#help-command)
- [Command Options](#command-options)
  - [Type Converters](#type-converters)


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


# Command Options
When it comes to CLI's you need to be able to accept user input. That's where the `options` paramter comes in

Let's take our example from before, and add an option the user can type in to be printed instead of "Hello, World!"

```py
@cli.script("greet", options=["name"])
def greet(name):
    '''Command that greets someone'''
    print(f"Hello, {name}!")
```
```
$ python3 example.py greet name=Sean
Hello, Sean!
```

Easy as that! Options are specified on the command line with `[OPTION_NAME]=[OPTION_VALUE]`.
All options specified in the options list will be passed to the function as arguement with the same name.

In the above example, the `name` option is required for the command execute.

```
$ python3 example.py greet
greet() missing 1 required positional argument: 'name'
```

If you add a default value to the arguement, the option becomes optional
```py
@cli.script("greet", options=["name"])
def greet(name="Joseph Joestar"):
    '''Command that greets someone'''
    print(f"Hello, {name}!")
```

```
$ python3 example.py greet name=Sean
Hello, Joseph Joestar!
```

## Type Converters
Typically, you don't want numbers, booleans, lists, represented as just strings. Arc provides type conversions that will convert the input to your desired type before passing it on to the command's function. If you've used Flask before, it's URL converters work in essentially the same way
```py
@cli.script("number_type", options=["<int:number>"])
def number_type(number):
    '''Command that prints the type of a number'''
    print(type(number))
```

```
$ python3 example.py number_type number=5
<class 'int'>
```
Check out [conveters.md](./converters.md) for more in depth info