# Options and Flags
- [Options and Flags](#options-and-flags)
  - [Command Options](#command-options)
  - [Flags](#flags)
    - [Flag example](#flag-example)
    - [Without using a flag](#without-using-a-flag)
    - [Using a flag](#using-a-flag)

## Command Options
When it comes to CLI's you need to be able to accept user input. That's where the `options` paramter comes in

Let's take our example from before, and add an option the user can type in to be printed instead of "Hello, World!"

```py
@cli.script("greet", options=["name"])
def greet(name):
    '''Command that greets someone'''
    print(f"Hello, {name}!")
```
```
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
@cli.script("greet", options=["name"])
def greet(name="Joseph Joestar"):
    '''Command that greets someone'''
    print(f"Hello, {name}!")
```

```
$ python3 example.py greet
Hello, Joseph Joestar!
```

## Flags
While you can use options for boolean values, flags are perferrable. Flags look like your typical unix command line switch `--flag_name`. If they are present in your command, the value passed to your script will be true, otherwise it will be false
### Flag example
Let's use the example from above to demo how a flag might work
### Without using a flag
```py
@cli.script("hello", options=["name", "<sbool:reverse>"]) # use the sbool converter to convert the string "True" to a boolean True
def hello(name, reverse=False): # set a default value, so you only need to specify when it's true
    '''Command that prints greets someone'''
    if reverse:
        name = name[::-1]
    print(f"Hello, {name}!")

cli()
```
```
$ python3 example.py hello name=Sean reverse=True
Hello, naeS!
```

### Using a flag
```py
@cli.script("hello", options=["name"], flags=["--reverse"])
def hello(name, reverse):
    '''Command that prints greets someone'''
    if reverse:
        name = name[::-1]
    print(f"Hello, {name}!")

cli()
```
```
$ python3 example.py hello name=Sean
Hello, Sean!
```
The script prints exactly the same, just as before, now adding the flag
```
$ python3 example.py hello name=Sean --reverse
Hello, naeS!
```
While using an option for this is perfectly functional, using a flag is a little cleaner