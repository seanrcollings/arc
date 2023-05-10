
You can define error handlers for your application. Error handlers are functions that are called when an error occurs in your application. You can define error handlers for specific error types or for all errors.

```py title="examples/errors/error_handlers.py"
--8<-- "examples/errors/error_handlers.py"
```

```console
--8<-- "examples/outputs/errors/error_handlers"
```

Handlers are called for relavent errors in reverse to the order they are defined. If you define a handler for a general error type, then a handler for a specific error type, the more specific handler will be called first.


## Bubbling Errors
If a particular error can't be handled by the current error handler, it will be passed to the next error handler. This is called bubbling. If no error handler can handle the error, the error will be passed to the default error handler.

```py title="examples/errors/bubbling.py"
--8<-- "examples/errors/bubbling.py"
```

```console
--8<-- "examples/outputs/errors/bubbling"
```

## Default Error Handling Behavior
If no error handler is defined, *arc* will use the default error handling behavior:

- For internal errors (errors that derive from `#!python arc.errors.ArcError`), a formatted message for the error will be printed to the console and then the application will exit with a non-zero exit code.
- All other errors will be bubbled to the Python runtime & a traceback will be printed to the console. Since this isn't a particularly graceful exit, it's recommended that you define error handlers for your application.

