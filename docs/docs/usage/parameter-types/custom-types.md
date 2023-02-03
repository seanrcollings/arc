
## Implement Your Own Type
By implmenting a simple protocol, your custom classes can be easily used as the type of an *arc* parameter.

### Example

When implementing your own types, you can make them compatible with arc by implementing the `#!python __convert__()` class method. *arc* will call this with the input from the command line (or some other [source]()), and you are expected to parse the input and return an instance of the type. For example,

```py title="custom_type.py"
--8<-- "examples/custom_type.py"
```
```console
--8<-- "examples/outputs/custom_type"
```

Some notes about custom types:

In additon to `value`, you can also add the following arguments to the signature (in the given order, but the names don't need to match):

- `info`: Description of the provided type. Instance of `#!python arc.types.TypeInfo`
- `ctx`: The current execution context. Instance of `#!python arc.context.Context`

### Context Managers

Any type that is considered a context manager (by `#!python contextlib.contextmanager()`) will be opened before the command callback executes, and then closed after the command executes

```py title="examples/context_manager.py"
--8<-- "examples/context_manager.py"
```

```console
--8<-- "examples/outputs/context_manager"
```

!!! Note
    Note that the return value of `__enter__()` is important here, because *it* is the value that is passed to the command.

## Type Aliases
Type aliases are the way in which *arc* implements support for builtin and standard library Python types, but can also be used for any type. You can use type aliases to provide support fo any third party library types. For example, supporting numpy arrays
```py
import arc
from arc.types import Alias
import numpy as np

# Inherits from Alias. The 'of' parameter declares what types(s) this
# alias handles (can be a single type or tuple of types).
# Reads like a sentence: "NDArrayAlias is the Alias of np.ndarray"
class NDArrayAlias(Alias, of=np.ndarry):

    @classmethod
    def __convert__(cls, value: str):
        return np.ndarray(value.split(","))


@arc.command()
def main(array: np.ndarray):
    arc.print(repr(array))


main()
```
```console
$ python example.py x,y,z
array(['x', 'y', 'z'], dtype='<U1')
```
All other principles about custom types hold for alias types.

Note that this is a simplified example, a more complete implementation would support the use of generics using `#!python numpy.typing`
## Generic Types
TODO
