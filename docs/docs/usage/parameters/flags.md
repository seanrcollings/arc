Flags are similar to [options](./options.md) as they are referenced by name, but they can only represent a boolean value (True / False) and do not recieve an associated value.

Flags are defined by annotating an argument with the `#!python bool` type.

```py title="examples/parameter_flag.py"
--8<-- "examples/parameter_flag.py"
```


```console
--8<-- "examples/outputs/parameter_flag"
```


!!! note "Default Values"
    Unlike arguments and options, flags are *always* optional. Thie is because they can only
    represent two possible values (True / False). Absence of the flag implies False; presence of the flag implies True. If a flag is given a default of `True` then this relationship is inversed.

## Alternative Syntax
Once again, like [arguments](./arguments.md) and [options](./options.md), flags also have an alternative syntax

```py
reverse: bool
```

```py
reverse = arc.Flag()
```
The `#!python bool` type is no longer required, but it's still generally recommended

[Check the reference for all the options that `arc.Flag()` can recieve](../../reference/params.md#arc.params.Flag)