# Special Script Names
Arc provides a couple special script names for particular functionality

- [Special Script Names](#special-script-names)
  - [anon script](#anon-script)
- [Configuration](#configuration)
- [Utilities too?](#utilities-too)

## anon script
Using the `anon` script name will allow you to create that you don't have to refer to by a specific name. As the name implies it's anonymous. If one is declared, when you execute the CLI without any paramters, or without a recognized script name, it will attempt to run the anonymous script

```py
@cli.subcommand(anon")
def cli_anon(name="Jotaro"): # Just like a normal script, if you want options to be optional, you have to proivde a default value
    print(f"Hello {name}!")
```

```
$ python example.py name=Sean
Sean
```

Both options and flags are available when using the anonymous scripts
[Example]("../examples/no_args_and_anon.py")

# Configuration
If you don't like the names I've chosen for the special scripts, you can modify them using the [.arc file or editing the Config object](./configuration.md). To change each special script's name, set it's respective config value. Each name is the default name, followed by `_identifier`
For example, `anon` config is `anon_identifier`

# Utilities too?
Yes, all the special script names work for both cli scripts and utility scripts. Simply start you command with `utility_name:` and dont' provide a script name like you would normally

