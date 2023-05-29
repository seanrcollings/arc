Type Arguments are a way for types to recieve additional information that can be used during type conversion. Type arguments are attached to a types using an `Annotated` type. They will generally take the form of.

```py
Annotated[Type, Type.Args(...)]
```

For example, the `#!python arc.types.File` type uses a type argument to specify the mode to open the file in.

```py
from typing import Annotated
import arc
from arc.types import File

@arc.command
def read(file: Annotated[File, File.Args("r")]):
    print(file.readline())
```

This tells *arc* that the `file` parameter should be opened in read mode.


??? TIP "Type Aliases"

    For convenience, *arc* provides several type aliases on the `File` type with the mode already defined. So the above example could be written as:


    ```py title="examples/file.py"
    --8<-- "examples/file.py"
    ```

    Note that using the alias doesn't actually prevent your from providing your own type arguments. So the following is also valid:

    ```py
    from typing import Annotated
    import arc
    from arc.types import File

    @arc.command
    def read(file: Annotated[File.Read, File.Args(encoding="ascii")]):
        print(file.readline())
    ```


Check out the [source](https://github.com/seanrcollings/arc/blob/main/arc/types/file.py#L28) for `#!python File.Args()` for information on how to define your own type arguments.


## Non *arc* types
If it's neccessary for a builtin or standard lib type to implement type arguments, they will be provided in the types package. For example:
```py title="examples/dates.py"
--8<-- "examples/dates.py"
```

Currently the following standard lib types have type arguments defined:

- `#!python datetime.datetime`: `#!python arc.types.DateTimeArgs`
- `#!python datetime.date`: `#!python arc.types.DateArgs`
- `#!python datetime.time`: `#!python arc.types.TimeArgs`
- `#!python int`: `#!python arc.types.IntArgs`


## When to Use Type Arguments

Type arguments should be used to provide information that is necessary **during type construction**. For example:

- `#!python arc.types.File` uses a type argument to specify the expected file mode. This is necessary because the `#!python File` type needs to know the file mode before it can be opened.
- `#!python datetime.datetime` type uses a type argument to specify the expected format of the input string. This is necessary because the `#!python datetime.datetime` type needs to know the format of the input string before it can be converted to a datetime object. In all other cases


If the information isn't needed until **after** the type has been constructed, then you should probably opt for a [Type Middleware](./type-middleware.md)
