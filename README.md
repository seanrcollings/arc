# ARC: A Regular CLI
A tool for building easy, and highly extendable CLI systems for Python 3.8

# Docs
- [Getting Started](docs/getting_started.md)
- [Utilities](docs/utilities.md)
- [Type Converters](docs/converters.md)
- [Context Managers](docs/context_mangers.md)

# Installation

From github
```
$ git clone https://github.com/seanrcollings/cli
$ pip install -e cli
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

```
$ python example.py hello
Hello, World!
```


Reference [getting started](docs/getting_started.md) for more info

