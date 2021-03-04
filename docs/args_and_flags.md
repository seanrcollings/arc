# Arguments and Flags
## Command Argumaents
When it comes to CLI's you need to be able to accept user input. Arc will look at the arguements that the function accepts to determine the possible arguments for the command.

Let's take our example from before, and add an option so the user can enter in a name instead of "Hello, World!"

```py
from arc import CLI
cli = CLI()

@cli.command()
def greet(name):
    '''Command that greets someone'''
    print(f"Hello, {name}!")

cli()
```
```out
$ python3 example.py greet name=Sean
Hello, Sean!
```

Easy as that! Arguments are specified on the command line with `[OPTION_NAME]=[OPTION_VALUE]`.
All arguments specified in the arguments list will be passed to the function as arguement with the same name.

In the above example, the `name` option is required for the command execute.

```
$ python3 example.py greet
greet() missing 1 required positional argument: 'name'
```

If you add a default value to the arguement, the option becomes optional
```py
from arc import CLI
cli = CLI()

@cli.command()
def greet(name="Joseph Joestar"):
    '''Command that greets someone'''
    print(f"Hello, {name}!")

cli()
```

```out
$ python3 example.py greet
Hello, Joseph Joestar!
```

## Type Conversion
Arc supports argument type conversion. Refer to [docs/converters.md](./converters.md) for more information

## Flags
Flags are specified by giving a function argument a `bool` type hint. Flags look like your typical unix command line switch `--flag_name`.

### Using a flag
```py
from arc import CLI
cli = CLI()

@cli.subcommand()
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

The command prints exactly the same, just as before, now adding the flag
```out
$ python3 example.py hello name=Sean --reverse
Hello, naeS!
```

By default, flags are considered `False` when not passed, and `True` when passed. This can be swapped by providing the arguments with the default value of `True`

Note that flags are actually just syntatic suguar for arguments, so writing:
```
$ python3 example.py hello name=Sean reverse=true
```
Would have the same result


## Kebab Case
Arc also supports using `kebab-case` for command names, arguments, and flags. For example:
```py
from arc import CLI
cli = CLI()

@cli.subcommand()
def hello_kebab(fist_name, reverse_name: bool):
    '''Command that prints greets someone'''
    if reverse:
        name = name[::-1]
    print(f"Hello, {name}!")

cli()
```
We could execute this like we would normally
```
$ python3 example.py hello_kebab first_name=Sean --reverse_name
```
Or we could replace it with `kebab-case`
```
$ python3 example.py hello-kebab first-name=Sean --reverse-name
```
Both are equally valid and have the same result