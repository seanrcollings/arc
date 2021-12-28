In *arc*, callbacks are a way to encapsulate shared functionality across multiple commands.

## Example

```py title="examples/callback_example.py"
--8<-- "examples/callback_example.py"
```

```console
--8<-- "examples/outputs/callback_example"
```

???+ tip
    Any function valid as a `#!python contextlib.contextmanager()` should be a valid callback function. Note that the only requirement is that the function *must* yield. If it does not yield, it will fail at execution.

## Callback Inheritance
