# Configuring an Arc app
| Config             | Purpose                                                                                         |                     Default                      |
| ------------------ | ----------------------------------------------------------------------------------------------- | :----------------------------------------------: |
| utility_seperator  | Determines what character (or series of characters) seperates a utility name from a script name |                       ":"                        |
| option_seperator   | Determines what character (or series of characters) seperates a option name from it's value     |                       "="                        |
| log                | Determines whether or not log messages get output to the console                                |                      False                       |
| debug              | Determines whether or not debug messages are output to the console                              |                      False                       |
| converters         | List of available type converters to be used to convert options                                 | [converters](./converters.md#builtin-converters) |
| flag_denoter       | Determines what character (or series of characters) flags begin with                            |                       "--"                       |
| no_args_identifier | Determines the name of the script that will run if there are no args                            |                    "no)args"                     |
| anon_identifier    | Determines the anonymous script (one that can be run without a name)                            |                      "anon"                      |

## Configure in Code
You can configure certain aspects of an Arc app through the Config object defined in [arc/config.py](../src/arc/config.py)
```py
from arc import CLI, Config
Config.log = True
cli = CLI()

@cli.script("hello")
def hello():
    '''Command that prints Hello World'''
    print("Hello, World!")

cli()
```
```
$ python3 example.py hello
Hello, World!
Completed in 0.00s
```
Because log was set to true, it reported it's runtime after completion. It is generaly reccomended that you set configs at the top of a file, before creating the CLI, but it is possible to do it afterwards.

## .arc file
You can also create a .arc config file
This:
```
# .arc file
log=True # comments are ignored!

```
Would have the same result as the example above

Arc will default to looking for a file called .arc in the current directory. But you can specify a different name:
```py
from arc import CLI
cli = CLI(arcfile="myacrfile")
```