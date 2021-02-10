# Commands
This page will go over the the ins and outs of the commands / subcommand API.

# Creating a Namespace
At it's core, ARC centers around creating Command namespaces
```py x
from arc import namespace

foo = namespace("foo")
```

## Creating a Command
Commands are created using Python decorators. A function becomes a command using the `foo.command()` decorator. You can pass a name into the command decorator. If there isn't an explicit name, the function's name will be used. This will be the name used to execute the command.

```py x
@foo.subcommand()
def hello():
    print("Hello, World!")
```

## Running the Command
To run the command, you can pass it into the `run` function exported by ARC 
```py x
run(foo)
```
We'll get into the other things that the `run` function can do for you later

## Putting it together
```py
from arc import namespace, run

foo = namespace('foo')

@foo.subcommand()
def hello():
    '''Command that prints Hello World'''
    print("Hello, World!")

run(foo)
```

```out
$ python example.py hello
Hello, World!
```

## Nesting Commands
While the `namespace` function is a way for the developer to explicitly declare a namespace, the `@foo.subcommand()` decorator also creates a namespace! This allows for very easy command nesting. Let's take the example from before and add a nested command to the `hello` namespace.

```py
from arc import namespace, run

foo = namespace('foo')

@foo.subcommand()
def hello():
    '''Command that prints Hello World'''
    print("Hello, World!")

@hello.subcommand() # use the hello namespace as this command's parent
def night():
    '''Command to greet people later 
    in the day'''
    print("Good evening good sir!")

run(foo)
```

```out
$ python example.py hello:night
Good evening good sir!
```

Each level of nesting from the namespace that was ran needs to be fully qaulified. Since the `night` command is in the namespace of `hello` which is in turn in the namespace of `foo` (the top level namespace) then the command is ran with `hello:night`. If we added another command in the `hello` namespace called `bar` it could be called with `hello:bar`. If we added it in the `night` namespace, it would be called with `hello:night:bar`

That's about all there is to it! You could add another command nested in the `hello` namespace, or another deeply nested command under the `night` namespace. There really is no hard limit to how far commands can be nested, but I would recommend to stick to 3 or fewer. Namespaces should be used to indicate that commands show some relation to each other, but serve a different function. If you need to modify the way a single command behaves, use [args and flags](./args_and_flags) for that. 

# What's the CLI object about then?
If you've read the README or getting started, you would have seen a `CLI` object being used to make commands. The CLI object essentially acts as a "top level namespace" for your tool and a convenience wrapper around calling the `run` function. We could use the CLI to rewrite the previous example as follows:

```py
from arc import CLI

cli = CLI()

@cli.subcommand()
def hello():
    '''Command that prints Hello World'''
    print("Hello, World!")

@hello.subcommand()
def night():
    '''Command to greet people later 
    in the day'''
    print("Good evening good sir!")

cli() # Equivelant to the 'run' function from before
```
```out
$ python example.py hello
Hello, World!
```
While these two may seem very similar, I would generally recommend to use the CLI approach for a few reasons:
- It doesn't require you to explicitly declare a namespace when you don't need to
- It makes the top-level or entry point of your CLI tool more clear for other people reading it
- All namespace are created via the `@foo.subcommand()` decorator - more consistency

# When to use `namespace()`
If I recommend to always use the CLI and `cli.subcommand()`, then why is the `namespace` function even part of the API? The primary reason is to allow tools to be more modular. Say you are creating a CLI for interacting with various parts of a website you run. If all the commands were contained in a single file, that could get quite large, and you'd probably want to break it up. The `namespace` function makes it easy for you to do so.

We could create a namespace for interacting with the db for example, and save it in `db.py`
```py
from arc import namespace

db = namespace("db") # the name we provide here is what will be used to navigate into this namespace

@db.subcommand() 
def create():
   ...

@db.subcommand()
def update():
   ...
```

Then in our main `cli.py`
```py x
from arc import CLI
from .db import db

cli = CLI()
cli.install_command(db)

#...

cli()
```

We could then run the create function like so:
```
$ python3 cli.py db:create
```

You may have noticed that while in the previous example we could run both `hello` and `hello:goodnight`, running `db` by itself won't work. Indeed if you try it, you'll get an error.

```
$ python3 cli.py db
The 'db' namespace cannot be executed on it's own. Check 'db:help' to get a list of available subcommands
```
That's no good! Thankfully ARC has a solution for this. By adding the following to the `db.py` module
```py x
@db.base()
def base_db():
    print("you can run the db command by itself!")
```
`db` will now be executable

```
$ python3 cli.py db
you can run the db command by itself!
```

If you've created a namespace with the decorator pattern, but only want it's subcommands to be executable you can write it like this:
```py x
from arc import CLI, NO_OP

cli = CLI()

@cli.subcommand()
def namespace():
    raise NO_OP

@namespace.subcommand()
def foo():
    print("foo")
```

This will make `namespace` non executable, but `namespace:foo` will be valid
