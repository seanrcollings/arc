# Utilities
Often, several Arc commands might have a commonality. For example, you might have several commands for interacting with a database (creating, dropping, crearing rows, deleting rows, etc...). But you also want them to be part of a bigger Arc app, but appropriately name spaced.

This is where utilities come in. The intention of utilities is to let you group similar commands together under a common banner. If you've ever used [Flask](https://palletsprojects.com/p/flask/) before, you'll be familiar with their route Blueprints, which are used to gather a set of routes under a common namespace. Utilities are the exact same concept.

## Quick Example
```py
from arc import CLI, Utility
converse = Utility('converse')
cli = CLI(utilities=[converse])
# can also use cli.install_utilities(converse) for the same effect

# regular cli command
@cli.script("greet")
def cli_greet(name="Joseph Joestar"):
    '''Command that greets someone CLI command'''
    print(f"Hello, {name}!")
    print(f"This command is associated with the global CLI")


# utility command
@converse.script("greet")
def utility_greet(name="Jotaro Kujo"):
    '''Command that greets someone utility command'''
    print(f"Howdy, {name}!")
    print(f"This command is associated with the 'converse' utility")

cli()
```

```out
$ python3 example.py greet name=Sean
Hello, Sean!
This command is associated with the global CLI
```
```out
$ python3 example.py converse:greet name=Sean
Howdy, Sean!
This command is associated with the 'converse' utility
```
As you can see, now we've got two different "greet" commands with different output.

Utility commands are accessed with `[UTILITY NAME]:[COMMAND]`. The utility name is defined on creation of the utility

## Help command
As with the base cli, utilities also all have a help command associated with them which will display all the commands installed on the utility and their docstring
```
$ python3 example.py converse:help
Utility converse
Execute this utility with converse:subcommand
:help
    Helper function for utilities
        Prints out the docstrings for the utilty's scripts

:greet
    Command that greets someone utility command
```
