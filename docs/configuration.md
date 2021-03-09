# Configuring an Arc app
| Config         | Purpose                                                                                          |                     Default                      |
| -------------- | ------------------------------------------------------------------------------------------------ | :----------------------------------------------: |
| namespace_sep  | Determines what character (or series of characters) seperates a utility name from a command name |                       ":"                        |
| arg_assignment | Determines what character (or series of characters) seperates an argument name from it's value   |                       "="                        |
| flag_denoter   | Determines what character (or series of characters) flags begin with                             |                       "--"                       |
| loglevel       | Sets the level of the `arc_logger`                                                               |                 `logging.WARNING                 |
| converters     | List of available type converters to be used to convert options                                  | [converters](./converters.md#builtin-converters) |


## Configure in Code
You can configure certain aspects of an ARC CLI through the Config object defined in [arc/config.py](../src/arc/config.py)
```py x
import logging
from arc import CLI, config
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
│   hello                                │
│                                        │
│  COMMAND:    ARGUMENT:    FLAG:        │
│                                        │
╰────────────────────────────────────────╯
────────────────────────────────────────
Hello, World!
────────────────────────────────────────
Completed in 0.0s

```
Because the loglevel was set to DEBUG, all developer information was printed out.

## .arc file
You can also create a .arc config file
This:
```
# .arc file
loglevel=10

```
Would have the same result as the example above

Arc will default to looking for a file called .arc in the current directory. But you can specify a different name in a number of ways:
```py x
from arc import CLI, config, run
cli = CLI(arcfile="myacrfile") # most common one
config.from_file("myarcfile") # useful when not using the CLI object
run(namespace, arcfile="myarcfile") # not generally reccomended
```