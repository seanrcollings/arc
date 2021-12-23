# ARC: A Regular CLI
A tool for building declartive, and highly extendable CLI systems for Python 3.9

# ARC Features
- Command line arguments based on python type hints
- Arbitrary command nesting
- Automatic `--help` documentation
- Dynamic command loading at runtime

# [Docs](http://arc.seanrcollings.com)

# Quick Start

```py
import arc

@arc.command()
def hello(name: str):
    """My first arc program!"""
    print(f"Hello {name}!")

hello()
```

```
$ python example.py hello Sean
Hello, Sean!
```

```
$ python example.py --help
USAGE
    manage.py [--help] [--] <name>

DESCRIPTION
    My first arc program!

ARGUMENTS
    name

OPTIONS
    --help (-h)  Shows help documentation
```
Reference [getting started](https://github.com/seanrcollings/arc/wiki) for more info
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

# Attribution
Much of arc's architecture is based on [click](https://click.palletsprojects.com/en/8.0.x/), though no code is lifted directly from click's source.
