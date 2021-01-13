# ARC: A Regular CLI
A tool for building easy, and highly extendable CLI systems for Python 3.8

# Docs
- [Changelog](docs/changelog.md)
- [Getting Started](docs/getting_started.md)
- [Utilities](docs/utilities.md)
- [Type Converters](docs/converters.md)
- [Context Managers](docs/context_mangers.md)
- [Special Script Names](docs/special_script_names.md)
- [Configuration](docs/configuration.md)

# Installation

```
$ pip install arc-cli
```

Clone for development
```
$ git clone https://github.com/seanrcollings/arc
$ pip install -e arc
```


# Quick Start

```py
from arc import CLI

cli = CLI()

@cli.script("hello")
def hello():
    print("Hello, World!")

cli()
```
Reference [getting started](docs/getting_started.md) for more info

```
$ python example.py hello
Hello, World!
```

# Tests
Run the full test suite with
```
$ python3 -m tests
```

Run a specific test case with
```
$ python3 -m tests [TEST CASE]
```




# My Goals
- Make a fully functioning, easy to use CLI creator
- Teach myself how to upload and maintain package on PyPi
- Do not rely on **any** third party packages (crazy, I know)


# TODO
- Make the parser better / more feature rich (allow it to have context of the cli application)
- finish File type