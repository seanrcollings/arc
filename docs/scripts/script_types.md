# Arc Script Types
# Keyword Script
Default script type. Assumes that input is in the form `optionname=value. Will throw an error if
given any orphaned options. Will except flags normally
## Examples

```python
from arc import CLI
from arc import ScriptType as st
cli = CLI()

@cli.script("greeting", st.KEYWORD) # Since it is the default, specifying here is optional
def test(name="Jotaro Kujo");
    print(f"Greeting, {name}!")

cli()
```
```
$ python3 example.py greeting name="Sean"
Greeting, Sean!
```
Keyword scripts also accept `**kwargs` as the final arguement. If it is any other argument, Arc will throw an error. Does not accept `*args`
```python
from arc import CLI
from arc import ScriptType as st

cli = CLI()

@cli.script("greeting", st.KEYWORD)
def test(name="Jotaro Kujo", **kwargs);
    print(f"Greeting, {name}!")
    if len(kwargs) > 0:
        for key, val in kwargs.items():
            print(key, val)

cli()
```
```
$ python3 example.py greeting name="Sean" age=19 occupation="Programmer"
Greeting, Sean!
age 19
occupation Programmer
```

# Positional Script
Assumes input in the form of `value1 value2 value3`. Acts simliarrly to positional funciton arguments in Python and will be passed in the order recieved. Will throw an error if any positional options are given.

## Examples
``
Keyword scripts also accept **kwargs as the final arguement. If it is any other argument, Arc will throw an error
```python
from arc import CLI
from arc import ScriptType as st

cli = CLI()

@cli.script("greeting", st.POSITIONAL)
def test(name="Jotaro Kujo");
    print(f"Greeting, {name}!")

cli()
```
```
$ python3 example.py greeting Sean
Greeting, Sean!
```
Positional Scripts also accept `*args` as the final argument. If it is any other argument, Arc will throw an error. Does not accept `**kwargs`
```python
from arc import CLI
from arc import ScriptType as st

cli = CLI()

@cli.script("greeting", st.KEYWORD)
def test(name="Jotaro Kujo", *args);
    print(f"Greeting, {name}!")
    if len(kwargs) > 0:
        for val in arg:
            print(val)

cli()
```
```
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