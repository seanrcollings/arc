# Options and Flags

## Command Options
When it comes to CLI's you need to be able to accept user input. Arc will look at the arguements that the function accepts to determine the possible options for the script.

Let's take our example from before, and add an option the user can type in to be printed instead of "Hello, World!"

```py
@cli.script()
def greet(name):
    '''Command that greets someone'''
    print(f"Hello, {name}!")
```
```out
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
@cli.script()
def greet(name="Joseph Joestar"):
    '''Command that greets someone'''
    print(f"Hello, {name}!")
```

```out
$ python3 example.py greet
Hello, Joseph Joestar!
```

## Flags
Flags are specified by giving a function argument a `bool` type hint. Flags look like your typical unix command line switch `--flag_name`.

### Using a flag
```py
@cli.script("hello")
def hello(name, reverse: bool):
    '''Command that prints greets someone'''
    if reverse:
        name = name[::-1]
    print(f"Hello, {name}!")

cli()
```

```out
$ python3 example.py hello name=Sean
Hello, Sean!
```

The script prints exactly the same, just as before, now adding the flag
```out
$ python3 example.py hello name=Sean --reverse
Hello, naeS!
```

