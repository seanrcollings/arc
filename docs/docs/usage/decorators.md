An *arc* decorator is a Python deocrator that **wraps** the execution of an *arc* command. They allow shared setup / teardown logic to be abstracted and re-used at will.

## Example
```py title="examples/decorator_create.py"
--8<-- "examples/decorator_create.py"
```

```console
--8<-- "examples/outputs/decorator_create"
```

## Decorator Inheritance
By default, subcommands inherit their parent's decorators.

```py title="examples/decorator_inherit.py"
--8<-- "examples/decorator_inherit.py"
```

```console
--8<-- "examples/outputs/decorator_inherit"
```

??? note "What's `children_only`?"
    This makes the decorator only be executed when running a child of the command
    it decorates, and not the command itself. This is especially useful with the
    root command object because by default, any decorator that decorates it (with inheritance on) will be executed twice: once for the global callback, and once fot the actual command's callback.

If this behavior is undesired, the decorator can be made non-inhertibale by setting `#!python inherit=False`
```py
import arc

@arc.decorator(inherit=False)
def cb():
    arc.print("before execution")
    yield
    arc.print("after execution")
```
This decorator must be applied explicitly to all commands it should wrap

Alternativley, a decorator can be removed from a single subcommand (and any of it's children) by decorating the subcommand with `#!python @decorator.remove`