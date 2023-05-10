Type Arguments are a way for types to recieve additional information that can be used during type conversion.


Type arguments are attached to a types using an `Annotated` type. They will generally take the form of.

```py
Annotated[Type, Type.Args(...)]
```

Currently, *arc* only usess type arguments for the `File` and `Stdin` types.

```py
from typing import Annotated
import arc
from arc.types import File

@arc.command
def read(file: Annotated[File, File.Args("r")]):
    print(file.read())
```

This tells arc that the `file` parameter should be opened in read mode.


There are convenience classes for the `File` and `Stream` types that can be used instead of the `Annotated` type.


```py title="examples/file.py"
--8<-- "examples/file.py"
```

Check out the [source](https://github.com/seanrcollings/arc/blob/main/arc/types/file.py#L28) for `#!python File.Args()` for information on how to define your own type arguments.

