*arc* supports a simple dependency injection system for commands.

```py title="examples/dependency.py"
--8<-- "examples/dependency.py"
```

```console
--8<-- "examples/outputs/dependency"
```

Note that arguments whose values are discovered
via dependency injection do not have associated command line
parameters. You can see this by inspecting the `--help` for the command.

```console
--8<-- "examples/outputs/dependency_help"
```
No `value` argument!


## Type dependencies
A type can be denoted to be a dependency by implementing the `#!python __depends__()` class method.

```py title="examples/type_dependency.py"
--8<-- "examples/type_dependency.py"
```

```console
--8<-- "examples/outputs/type_dependency"
```
!!! warning
    If you implement this method, then this type cannot be used as the type of any other kind
    of parameter.

*arc* uses this feature to make various components available to your commands:

- [`arc.Context`](../../reference/runtime/context.md)
- [`arc.prompt.Prompt`](../../usage/user-input.md)
- [`arc.types.State`](../command-state.md)
