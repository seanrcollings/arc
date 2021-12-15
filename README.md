# ARC: A Regular CLI
A tool for building declartive, and highly extendable CLI systems for Python 3.9

# ARC Features
- Command Line arguments using Python function arguments and type hints
- Command Namespacing
- Help Documentation Generation
- User-extension via Dynamic namespace loading

# Docs
- [Docs](http://arc.seanrcollings.com)
- [Wiki](https://github.com/seanrcollings/arc/wiki)
- [Changelog](https://github.com/seanrcollings/arc/wiki/Changelog)

# Installation

```
$ pip install arc-cli
```

Clone for development
```
$ git clone https://github.com/seanrcollings/arc
$ poetry install
```


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
    --help (-h)  Shows help documentation
    <name>
```
Reference [getting started](https://github.com/seanrcollings/arc/wiki) for more info

# Tests
Tests are written with `pytest`
```
$ pytest
```
