# ARC Context
ARC context enables you to pass data into your function through an argument, without exposing that argument to the external interface.

Context is a dictionary of key-value pairs that you pass when creating the CLI, a namespace, or subcommand. ARC knows what argument to map the context to by specifying the type of the argument to be `Context`
```py
from arc import CLI, Context

cli = CLI(context={'test': 1})

@cli.command()
def context_example(ctx: Context): # ctx could be replaced with anything
     # can be accessed like a dictionary or an attribute
    print(ctx.test)
    print(ctx['test'])

cli()
```

```out
$ python3 example.py context_example
1
1
```
Note that you cannot overwite the value of `ctx` from the command line
```out
$ python3 example.py context_example ctx=2
Option 'ctx' not recognized
```

## Context Propagation
Context can be declared at any level of command decleration, and is passed down from parent commands. At each level, the parent's context and the current context are merged, with the current context taking precedent over the parent's context if keys overlap.

```py
from arc import CLI, Context, namespace

foo = namespace("foo", context={'test2': 2}) # declare the namespace's context
cli = CLI(context={'test': 1})
# when it's installed, it
# inherits it's parents context, so foo's context
# would be : {'test': 1, 'test2': 2}
cli.install_command(foo)

# this also inherit's it's parent's context
# but overwrites a key
@foo.subcommand(context={"test": 5})
def context_example(ctx: Context):

    print(ctx.test)
    print(ctx.test2)

cli()
```

```out
$ python3 example.py foo:context_example
5
2
```

## Context Inheritance
Context can also be subclassed for additional functionality.

```py
from arc import CLI, Context


class MyContext(Context):
    def punch(self):
        print(f"ORA ORA, {self.name}")


cli = CLI(context={"name": "DIO"})


@cli.command()
def punch(ctx: MyContext):
    ctx.punch()


cli()
```


```out
$ python3 example.py punch
ORA ORA, DIO
```

### Typing
Context Inheritance is also useful for typing your context object for type checkers like `mypy`

```py
from arc import CLI, Context

class MyContext(Context):
    name: str

cli = CLI(contex={"name": "DIO"})

@cli.command()
def greet(ctx: MyContext):
    # mypy will recognize the type of ctx.name
    # as string, so the following line will not
    # result in an error
    print("Hello " + ctx.name)
```
