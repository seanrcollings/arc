# CLI README
A tool for building easy, and highly extendable CLI systems for Python 3.8

# Installation

From github
```
$ git clone https://github.com/seanrcollings/cli
$ pip install -e cli
```

# Getting Started

Quick example

```py
from cli import CLI

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