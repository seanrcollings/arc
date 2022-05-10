In *arc*, callbacks are a way to encapsulate shared functionality across multiple commands.

## Example

```py title="examples/callback_example.py"
--8<-- "examples/callback_example.py"
```

```console
--8<-- "examples/outputs/callback_example"
```
!!! note
    The examples used in this document will generally `yield` to show that callbacks *wrap* the
    execution of a command. However, they are not required to do this and can just be simple functions
    if they only need to perform setup before the command runs.

## Creating Callbacks
As seen above, all `Command` objects have a `callback()` method for creating callbacks for that command. This is actually an alias for a two step process, that becomes more useful when using callbacks in a [multi-command CLI](cli.md)
```py title="examples/callback_create.py"
--8<-- "examples/callback_create.py"
```


```console
--8<-- "examples/outputs/callback_create"
```
`#!python callback.create()` transforms a function into a `Callback` object. Then, by deocorating a command with the callback, it gets added as a callback to that command


## Callback Inheritance
By default, When using `#!python arc.CLI()`, callbacks are inherited by any subcommand of the command it is added to. For Example:

```py title="examples/callback_inherit.py"
--8<-- "examples/callback_inherit.py"
```

```console
--8<-- "examples/outputs/callback_inherit"
```

- `c2` Executed the global callback because it inherited it from the `CLI`
- `c1` executed the global callback because it inherited it from the `CLI` and it executed it's own callback
- `c1:sub` executed the global callback because it inherited it from the `CLI` and it executed it's parent's (`c1`) callback.

Callback inheritance can be stopped in two ways.

- Set `#!python inherit = False` when creating the callback. When a callback is non-inhertiable, it can still be added to any command by deocrating the command with it.
- Use `#!python @callback.remove()` or `#!python @arc.callback.remove(<callbacks...>)` to remove a callback from a particular command and any of it's subcommands.

Let's modify the above example to remove all callbacks from `c1:sub`

```py title="examples/callback_inherit2.py"
--8<-- "examples/callback_inherit2.py"
```

```console
--8<-- "examples/outputs/callback_inherit2"
```

- `c2` executed the global callback because it inherited it from the `CLI`
- `c1` executed the global callback because it inherited it from the `CLI` and it executed it's own callback
- `c1:sub` executed neither callback because it removed the `CLI` callback with `#!python @global_callback.remove` and `c1_callback` is non-inhertiable.


