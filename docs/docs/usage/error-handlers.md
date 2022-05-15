Error handlers allow you to create modulare, composable, re-usable error handling code for you application.

```py title="examples/error_handlers.py"
--8<-- "examples/error_handlers.py"
```

```console
--8<-- "examples/outputs/error_handlers"
```

The handler defined handles `RuntimeError`s so it was executed and handled the error. Because there was an error handler registered, no stack trace was printed to the console, and the application exited with a 0 exit code.

## Re-Raising

If the handler can't handle a particular error, you can `raise` the exception again (or even raise a new exception). This will cause it to continue down the list of excetion handlers until it finds one that does handle the exception. If none are found, the exception will be handled by *arc's* default error-handling behavior.


## Relationship to Callbacks
Under the hood, exception handlers *are* [callbacks](./callbacks.md). For example, we could take the example from above and convert it to use a callback.

```py title="examples/error_handlers_callback.py"
--8<-- "examples/error_handlers_callback.py"
```

```console
--8<-- "examples/outputs/error_handlers_callback"
```

Error handlers are simply some *syntatic sugar* on top of callbacks to provide a slightly nicer interface. And as such, all of the principles about callbacks also apply to error handlers

- Like callbacks, error handlers are inherited
    - Can be disabled with `#!python @command.handle(*exceptions, inherit=False)`
    - Can be removed with `#!python @handler.remove`
