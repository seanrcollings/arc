# ARC: A Regular CLI
A tool for building easy, and highly extendable CLI systems for Python 3.8

# Docs
- [Getting Started](docs/getting_started.md)
- [Utilities](docs/utilities.md)
- [Type Converters](docs/converters.md)
- [Context Managers](docs/context_mangers.md)

# Installation

From GitHub
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

# Tests
Run the full test suite with
```
$ python3 -m tests
```

Run a specific test case with
```
$ python3 -m tests [TEST CASE]
```



Reference [getting started](docs/getting_started.md) for more info

