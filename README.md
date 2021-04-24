# ARC: A Regular CLI
A tool for building declartive, and highly extendable CLI systems for Python 3.9

# ARC Features
- Automatic type convertsion
- Command Namespacing
- Help Documentation Generation
- User-extension via Dynamic namespace loading

# Docs
- [Changelog](docs/changelog.md)
- [Getting Started](docs/getting_started.md)
- [CLI Arguments](docs/args_and_flags.md)
- [Type Conversion](docs/data_types.md)
- [Commands](docs/commands/commands.md)
- [Configuration](docs/configuration.md)
- [Contest](docs/context.md)
- [Autoloading](docs/autloading.md)
- [Autcompletion](docs/autocompletion.md)


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

@cli.command()
def hello():
    print("Hello, World!")

cli()
```

```
$ python example.py hello
Hello, World!
```
Reference [getting started](docs/getting_started.md) for more info

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

