# Arc Command Types
Arc provides several different Command Types that change the way that input is interpreted
#Keyword Command
Default command type. Assumes that input is in the form `argname=value.` Will throw an error if
given any orphaned options. Will except flags normally
## Examples

```python
from arc import CLI
from arc import CommandType as ct
cli = CLI()

@cli.subcommand(greeting", ct.KEYWORD) # Since it is the default, specifying here is optional
def test(name="Jotaro Kujo"):
    print(f"Greeting, {name}!")

cli()
```
```out
$ python3 example.py greeting name="Sean"
Greeting, Sean!
```
Keyword commands also accept `**kwargs` as the final arguement. If it is any other argument, Arc will throw an error. Does not accept `*args`
```python
from arc import CLI
from arc import CommandType as ct

cli = CLI()

@cli.subcommand(greeting", ct.KEYWORD)
def test(name="Jotaro Kujo", **kwargs):
    print(f"Greeting, {name}!")
    if len(kwargs) > 0:
        for key, val in kwargs.items():
            print(key, val)

cli()
```
```out
$ python3 example.py greeting name="Sean" age=19 occupation="Programmer"
Greeting, Sean!
age 19
occupation Programmer
```

# Positional Command
Assumes input in the form of `value1 value2 value3`. Acts similarly to positional funciton arguments in Python and will be passed in the order recieved. Will throw an error if any keyword options are given.

## Example
```python
from arc import CLI
from arc import CommandType as ct

cli = CLI()

@cli.subcommand(greeting", ct.POSITIONAL)
def test(name="Jotaro Kujo"):
    print(f"Greeting, {name}!")

cli()
```
```out
$ python3 example.py greeting Sean
Greeting, Sean!
```
Positional Scripts also accept `*args` as the final argument. If it is any other argument, Arc will throw an error. Does not accept `**kwargs`
```python
from arc import CLI
from arc import CommandType as ct

cli = CLI()

@cli.subcommand(greeting", ct.POSITIONAL)
def test(name="Jotaro Kujo", *args):
    print(f"Greeting, {name}!")
    if len(args) > 0:
        for val in args:
            print(val)

cli()
```
```out
$ python3 example.py greeting "Sean" 19 "Programmer"
Greeting, Sean!
19
Programmer
```
# Raw Command
Raw commands won't do anything to the input and pass it to your function exactly as recieved. Essentially, it acts as just a wrapper around `sys.argv`. Primarily useful for when you want to take full control over how the input is interpreted for a specific command or namespace.
## Examples
```python
from arc import CLI
from arc import CommandType as ct

cli = CLI()

@cli.subcommand(raw", ct.RAW)
def test(*args):
    print("Here the input!")
    print(*args)

cli()
```
```
$ python3 example.py raw option=val orphan --flag option="val with spaces"
Here's the input!
example.py raw option=val orphan --flag option=val with spaces
```


# Command type is inherited
Command types can be specified on the CLI, Utility, or Command level.
```py x
from arc import CLI, namespace, CommandType as ct

cli = CLI(command_type=ct.KEYWORD) # At CLI level

ns = namespace("namespace", command_type=ct.POSITIONAL) # at a namespace level

@ns.subcommand(greeting", ct.RAW)  # At Command level
def greeting(*args):
    print(args)
```
If the command type is not defined on the command, it inherits the type of it's parent namespace. 


## [Custom Scripts](./custom_command_type.md)

