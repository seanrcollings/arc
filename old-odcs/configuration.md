# Configuring an Arc app

## Contents
| Config         | Purpose                                                                                          |                     Default                      |
| -------------- | ------------------------------------------------------------------------------------------------ | :----------------------------------------------: |
| namespace_sep  | Determines what character (or series of characters) seperates a utility name from a command name |                       ":"                        |
| arg_assignment | Determines what character (or series of characters) seperates an argument name from it's value   |                       "="                        |
| flag_denoter   | Determines what character (or series of characters) flags begin with                             |                       "--"                       |
| loglevel       | Sets the level of the `arc_logger`                                                               |                 logging.WARNING                  |
| converters     | List of available type converters to be used to convert options                                  | [converters](./converters.md#builtin-converters) |


## Configure in Code
You can configure certain aspects of an ARC CLI through the Config object defined in [arc/config](../src/arc/config/__init__.py)
```py x
import logging
from arc import CLI, arc_config
config.loglevel = logging.DEBUG

cli = CLI()

@cli.subcommand()
def hello():
    '''Command that prints Hello World'''
    print("Hello, World!")

cli()
```
```
registered 'help' command to cli
registered 'hello' command to cli
╭────────────────────────────────────────╮
│                                        │
│   hello                                │# This portion will show colored
│                                        │# output of what the parser parsed
│  COMMAND:    ARGUMENT:    FLAG:        │# in the terminal
│                                        │
╰────────────────────────────────────────╯
────────────────────────────────────────
Hello, World!
────────────────────────────────────────
Completed in 0.0s

```
Because the loglevel was set to DEBUG, all developer information was printed out.

## File Configuration
You can also create a .arc config file. This:
```
loglevel=10
namespace_sep=::
```
Would have the same result as the example above. The file loading system expects simple `key=value` pairs, and will allow Python-style single line comments denoted with `#`.

Arc will default to looking for a file called .arc in the current directory. But you can specify a different name in a number of ways:
```py x
from arc import CLI, arc_config, run
cli = CLI(arcfile="myacrfile") # most common one
arc_config.from_file("myarcfile") # useful when not using the CLI object
run(namespace, arcfile="myarcfile")
```

# Creating a Config
If you're app has pretty simple configuration, it can probably use ARC's internal config system for itself. The `arc.config` module provides a `BaseConfig` class, along with the `Config` class that ARC uses.

## Basic example
```python
from arc.config import ConfigBase

class MyConfig(ConfigBase):
    # Define your configuration values
    # at the class level, like you would with a
    # dataclass
    favorite_color: str = "red" # can optionally provide a default value
    favorite_number: int # Given no default value, will default to None

    # Feel free to define any extra
    # functionality you may want on your objects
    def cards(self):
        print(f"Give me {self.favorite_number} {self.favorite_color} cards!")

# ConfigBase preforms type checking so:
config = MyConfig(favorite_number = 2)
config.favorite_number # 2
config.cards() # Give me 2 red cards!
```

`ConfigBase` preforms type checking, so:
```py
config = MyConfig(favorite_number = 2) # this is good
bad_config = MyConfig(favorite_number = 'flower') # this is not
```

## Loading Files
When you define a Config class, it comes with the `from_file` method for file loading. This will behave like it does on the `arc_config` object, but you can modulate it's behavior a bit by defining the `parse` method

```py
class MyConfig(ConfigBase):
    favorite_color: str = "red"
    favorite_number: int

    def parse(self, lines: list[str]) -> dict[str, Any]:
        # Recieves the lines of the loaded
        # file (with comments removed).
        # Expects you to return a dictionary of values
        # that correspond to the values in your config.
        # For example, for this config:
        {
           "favorite_color": "green",
           "favorite_number": 2
        }
        # would be a valid return statement.


```
