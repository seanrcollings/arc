# ARC: A Regular CLI
A tool for building declarative, and highly extendable CLI systems for Python 3.9

# ARC Features
- Command line arguments based on python type hints
- Arbitrary command nesting
- Automatic `--help` documentation
- Fully Extensible with custom middlewares,  types, validators, parameter configurations, etc...

# [Docs](http://arc.seanrcollings.com)

# Quick Start

```py
import arc

@arc.command
def hello(name: str):
    """My first arc program!"""
    arc.print(f"Hello {name}!")

hello()
```

```
$ python hello.py Sean
Hello, Sean!
```

```
$ python hello.py --help
USAGE
    hello.py [-h] [--] name

DESCRIPTION
    My first arc program!

ARGUMENTS
    name

OPTIONS
    --help (-h)  Displays this help message
```

# Installation

```
$ pip install arc-cli
```

Clone for development
```
$ git clone https://github.com/seanrcollings/arc
$ poetry install
```

# Tests
Tests are written with `pytest`
```
$ pytest
```
