# ARC: A Regular CLI
A tool for building declartive, and highly extendable CLI systems for Python 3.9

# ARC Features
- Automatic type convertsion
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
Reference [getting started](https://github.com/seanrcollings/arc/wiki) for more info

# Tests
Tests are written with `pytest`
```
$ pytest
```

