# Command Autoloading
ARC support dynamic loading of subcommands via the `CLI#autoload` method. For example:

```py x
# /home/user/timers.py
from arc import namespace

timers = namespace("timers")

@timers.subcommand()
def test():
    print("I've been autoloaded!")

```

```py x
# cli.py
from arc import CLI

cli = CLI()
cli.autoload("/home/users/timers.py")

cli()
```
Now we can run the `timers:test` command, without importing it directly
```
$ python cli.py timers:test
I've been autoladed!
```

`CLI#autoload` can accept an arbitrary number of paths to either files or directories. When given a file, it will do as above. When given a directory, it will attempt to load every file in that directory. In both cases, if no command is found, it will continue onto the next path rather than erroring.

## Restrictions
Autoloaded Commands cannot overide commands installed by normal means. This is to prevent a user from accidentally overwriting a part of a tool they where unaware of with their own code.

The `autoload` method is available on the `CLI` object and not on the more general `Command` object. As such, commands can only be autoloaded onto the root CLI object and not into sub-commands. This is a style choice to prevent confusion / over-engineered complexity. However, while I don't reccomend this, if you still want to use autoloading with a sub-command, you can by using the internal `Autoload` object:
```py
from arc import namespace
from arc.cli import Autoload

command = namespace("command")
Autoload(command, "/path/to/module").load()
```
Whatever commands are detected in `/path/to/module` will be installed on to the command object

## Motivation
- Allows for consumers of a tool to extend to tool for their own use, without having to actually dig into the sourcecode
- It's neat :)

