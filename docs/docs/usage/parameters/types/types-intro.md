*arc* uses argument type hints for data validation / conversion. For example, say we want to write a command that can sum two numbers together:
```py title="examples/add.py"
--8<-- "examples/add.py"
```

```console
--8<-- "examples/outputs/add"
```
if the input fails to validate, *arc* will report a user-friendly error for the type
```console
--8<-- "examples/outputs/add_error"
```

!!! note
    if a parameter does not specify a type, *arc* implicitly types it as `#!python str`.
