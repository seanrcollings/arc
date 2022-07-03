An `arc` decorator is a Python deocrator that `wraps` the execution of an `arc` command. They allow shared setup / teardown logic to be abstracted and re-used at will.

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

If this behavior is undesired, the decorator can be made non-inhertibale by setting `#!python inherit=False`
```py
import arc

@arc.decorator(inherit=False)
def cb():
    print("before execution")
    yield
    print("after execution")
```
This decorator must be applied explicitly to all commands it should wrap

Alternativley, a decorator can be removed from a single subcommand (and any of it's children) by decorating the subcommand with `#!python @decorator.remove`