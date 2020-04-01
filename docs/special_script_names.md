# Special Script Names
Arc provides a couple special script names for particular functionality

- [Special Script Names](#special-script-names)
  - [no_args script](#noargs-script)
  - [anon script](#anon-script)
- [Configuration](#configuration)
- [Utilities too?](#utilities-too)

## no_args script
Using the `no_args` script name will allow you to define a script to run when no arguments are passed to Arc


```py
@cli.script("no_args")
def cli_no_args():
    print("no_args here!")
```

```
$ python example.py
no_args here!
```
It should be noted that the `no_args` script cannot accept any options or flags, that is what the `anon` script is for
[Example]("../examples/no_args_and_anon.py")

## anon script
Using the `no_args` script name will allow you to define a script to run without a script name, but allows other arguements to be passed to the script.

```py
@cli.script("anon", options=["name"])
def cli_anon(name):
    print(name)
```

```
$ python example.py name=Sean
Sean
```

Both options and flags are available when using the anonymous scripts
[Example]("../examples/no_args_and_anon.py")

# Configuration
If you don't like the names I've chosen for the special scripts, you can modify them using the [.arc file or editing the Config object](./configuration.md). To change each special script's name, set it's respective config value. Each name is the default name, followed by `_identifier`
For example, `no_args` config is `no_args_identifier`

# Utilities too?
Yes, all the special script names work for both cli scripts and utility scripts. Simply start you command with `utility_name:` and dont' provide a script name like you would normally

