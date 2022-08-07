`#!python arc.State` is *arc's* primary way for sharing global data all throughout your application.

State is a dictionary of key-value pairs that you pass when executing you application. A command can then request access to the state object by annotating a argument with `State`
```py title="examples/state.py"
--8<-- "examples/state.py"
```

```console
--8<-- "examples/outputs/state"
```

Note that because the `State` type has a special meaning it will not be exposed to the external interface
```
--8<-- "examples/outputs/state_help"
```

## Subclassing `State`
State may also be sub-classed, and still maintain the same unique behavior. This is useful for providing additional functionality via attached methods, or provide type hinting support for static analyzers like mypy.

```py title="examples/state_inherit.py"
--8<-- "examples/state_inherit.py"
```

```console
--8<-- "examples/outputs/state_inherit"
```
