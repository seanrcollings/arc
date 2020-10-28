# Arc Script Types
# Keyword Script
Default script type. Assumes that input is in the form `optionname=value.` Will throw an error if
given any orphaned options. Will except flags normally
## Examples

```python
from arc import CLI
from arc import ScriptType as st
cli = CLI()

@cli.script("greeting", st.KEYWORD) # Since it is the default, specifying here is optional
def test(name="Jotaro Kujo"):
    print(f"Greeting, {name}!")

cli()
```
```out
$ python3 example.py greeting name="Sean"
Greeting, Sean!
```
Keyword scripts also accept `**kwargs` as the final arguement. If it is any other argument, Arc will throw an error. Does not accept `*args`
```python
from arc import CLI
from arc import ScriptType as st

cli = CLI()

@cli.script("greeting", st.KEYWORD)
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

# Positional Script
Assumes input in the form of `value1 value2 value3`. Acts simliarrly to positional funciton arguments in Python and will be passed in the order recieved. Will throw an error if any keyword options are given.

## Examples
```python
from arc import CLI
from arc import ScriptType as st

cli = CLI()

@cli.script("greeting", st.POSITIONAL)
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
from arc import ScriptType as st

cli = CLI()

@cli.script("greeting", st.POSITIONAL)
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
# Raw Script
Raw scripts won't do anything to the input and pass it to your function exactly as recieved. Essentially, it acts as just a wrapper around `sys.argv`. Primarily useful for when you want to take full control over how the input is interpreted for a specific script or utility.
## Examples
```python
from arc import CLI
from arc import ScriptType as st

cli = CLI()

@cli.script("raw", st.RAW)
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
# Legacy Script
Legacy Script is the original implementation of scripts and is not reccomended for use. It's not managed as throughly as the others. It can be configure to accept both
positional and keyword arguments.

# Script type is inherited
Script types can be specified on the CLI, Utility, or Script level.
```py x
from arc import CLI, Utility, ScriptType as st

cli = CLI(script_type=st.KEYWORD) # At CLI level

util = Utility("name", script_type=st.POSITIONAL) # at Utility level

@cli.script("greeting", st.RAW)  # At Script level
def greeting(*args):
    print(args)
```
If the script type is not defined on the script, it inherits the type of it's Parent container (Either the cli or a utility). In the case of a utility, if it also not defined, it inherits from the CLI which by default is `KEYWORKD`.
Keep in mind that when it comes to utilites, they must be registered to the CLI before registering any scripts to them if you want those scripts to inherit the `script_type` of the CLI.
## This Works:
```py x
from arc import CLI, Utility, ScriptType as st

util = Utility("name")
cli = CLI(utilities=[util], script_type=st.POSITIONAL)
# since util doesn't specify a script type,
# when it's registered it inherits it form the CLI

@util.script("greeting") # This script's script type would also be Positional
def greeting(*args):
    print(args)

```

## This Does not:
```py x
from arc import CLI, Utility, ScriptType as st

util = Utility("name") # util is created with Default script type

@util.script("greeting") # This script is created with the util's script type
def greeting(**kwargs):
    print(args)

cli = CLI(utilities=[util], script_type=st.POSITIONAL)
# Util's script type is changed, but the 'greeting' script would not be
# If other util scripts are defined below this point, they will recieve
# the POSITIONAL script type
```
To avoid this issue, it is generally best practice to define all your utilities, then register them the cli, then define the scripts
```py
from arc import CLI, Utility, ScriptType as st

util = Utility("name")
util2 = Utility("name2")
util3 = Utility("name3")
cli = CLI(utilities=[util, util2, util3], script_type=st.POSITIONAL)
# all would recieve the POSITIONAL script type

@util.script("greeting") # This script's script type would be Positional
def greeting(*args):
    print(args)

```
For Utilities split between multiple files, explictly defining their script type would be better.

## [Custom Scripts](./custom_script_type.md)

