`arc.types.State` is arc's primary way for sharing global data all throughout your application.

State is a dictionary of key-value pairs that you pass when creating the CLI, a namespace, or subcommand. arc knows what argument to map the state to by specifying the type of the argument to be `State`
```py
from arc import CLI, State

cli = CLI(state={'test': 1})

@cli.command()
def state_example(state: State):
    # can be accessed like a dictionary or an attribute
    print(state.test)
    print(state['test'])

cli()
```

```
$ python example.py state-example
1
1
```
Note that because the `State` type has a special meaning it will not be exposed to the external interface
```
$ python example.py state-example --help
USAGE
    example.py state-example [--help] [--]

ARGUMENTS
    --help (-h)  Shows help documentation
```

## State Propagation
State can be declared at any level of command decleration, and is passed down from parent commands. At each level, the parent's state and the current state are merged, with the current state taking precedent over the parent's state if keys overlap.

```py
from arc import CLI, State, namespace

foo = namespace("foo", state={'test2': 2}) # declare the namespace's state
cli = CLI(state={'test': 1})
# when it's installed, it
# inherits it's parents state, so foo's state
# would be : {'test': 1, 'test2': 2}
cli.install_command(foo)

# this also inherit's it's parent's state
# but overwrites a key
@foo.subcommand(state={"test": 5})
def state_example(state: State):

    print(state.test)
    print(state.test2)

cli()
```

```
$ python example.py foo:state-example
5
2
```

## State Sharing
State is shared amongst commands, so it's an easy way to share objects / data when executing a command *within* another command.
```py
import contextlib
from arc import CLI, State, Context

cli = CLI()


@contextlib.contextmanager
def open_db():
    obj = object()
    try:
        yield obj
    finally:
        del obj


@cli.command()
def command1(state: State, ctx: Context):
    # ctx.resource() opens context managers and
    # ensures they get closed
    state.db = ctx.resource(open_db())
    ctx.execute(command2)


@cli.command()
def command2(state: State):
    print(state.db)  # object is accessible here!


cli()

```

## State Inheritance
State can also be subclassed for additional functionality.

```py
from arc import CLI, State


class MyState(State):
    def punch(self):
        print(f"ORA ORA, {self.name}")


cli = CLI(state={"name": "DIO"})


@cli.command()
def punch(state: MyState):
    state.punch()


cli()
```


```
$ python example.py punch
ORA ORA, DIO
```
