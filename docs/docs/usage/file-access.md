One of the most common things that a CLI tool is likely to do, is take in a file name as input, and interact with that file in some way. *arc's* advanced typing system makes this trivial, with the details around ensuring the file exists, opening it, and closing it handled by *arc* for you.


*arc* provides this functionality through its [`#!python arc.types.File`](../reference/types/file.md) type. Let's use it to read out the first line of the source code's README.

```py title="examples/types/file.py"
--8<-- "examples/types/file.py"
```

```console
--8<-- "examples/outputs/types/file"
```

There are constants defined on `File` (like `File.Read` above) for all common actions (`Read`, `Write`, `Append`, `ReadWrite`, etc...). You can view them all in the [reference](../reference/types/file.md)
