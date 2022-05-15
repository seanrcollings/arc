In *arc*, callbacks are a way to encapsulate shared functionality across multiple commands.

In short, callbacks are:

- Reusable
- Composable
- Modular


## Creating Callbacks
Callbacks are created using the `#!python arc.callback.create()` function. This will wrap your provided function into a callback, which you then decorate a command with to register that callback to that command.


```py title="examples/callback_create.py"
--8<-- "examples/callback_create.py"
```

```console
--8<-- "examples/outputs/callback_create"
```

You can think of callbacks as *wrapping* the execution of a command. They can be used to perform any shared setup-code and any shared teardown code needed.

!!! tip
    The examples used in this document will generally `yield` to show that callbacks *wrap* the
    execution of a command. However, they are not required to do this and can just be simple functions
    if they only need to perform setup before the command runs.


### Callback Creation Shorthand
All `Command` objects have a `#!python callback()` method, so they above can be modified to:

```py title="examples/callback_example.py"
--8<-- "examples/callback_example.py"
```

```console
--8<-- "examples/outputs/callback_example"
```
In essence, all this method does is create the callback, and register it to the `Command` being referred to.


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
- Use `#!python @callback.remove()` or `#!python @arc.callback.remove(*callbacks)` to remove a callback from a particular command and any of it's subcommands.

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


## Error Handling
If you're going to be performing cleanup within a callback, it's generally advisable to wrap it in a `finally` block. This makes sure that the code is ran, regardless of whether or not the executed command succeeds.

You can also catch and handle exception within callbacks, but that is primarily the responsibilty of [error handlers](./error-handlers.md)
