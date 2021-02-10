# Scripts
Arc Scripts come several different flavors. Each flavor changes the way that input is interpreted and how
it will be passed to the users's function.

These are as follows:
- Keyword
- Positional
- Legacy
- Raw

Details on each can be seen [here](./script_types.md)

## Basic Example
```py
from arc import CLI

cli = CLI()

@cli.command()
def hello_world():
    print("Hello World!")

cli()
```

```out
$ python3 example.py hello_world
Hello World!
```

## Other notes
CLIs and utilities include a helper method to add scripts programmatically
```py

from arc import CLI
cli = CLI()

def func(name, age: int):
    print(f"I'm {name}, and I'm {age} years old")

cli.install_script("name_and_age", func)
cli()
```

```out
$ python3 example.py name_and_age name=Sean age=19
I'm Sean and I'm 19 years old
```
`install_script` accepts all the same arguments as the as `@cli.script`