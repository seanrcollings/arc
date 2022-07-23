The simplest *arc* program would look like this
```py title="hello_world.py"
--8<-- "examples/hello_world.py"
```
Which we can then execute directly!
```console
--8<-- "examples/outputs/hello_world"
```

Let's break this down to better understand what exactly is going on.

1. `#!python @arc.command()` is a Python decorator that transforms a function into an *arc* command.
2. `#!python def main()` is just a simple Python function
3. `#!python main()` while this make look like we're calling the `main` function, because the function has been transformed into a command, we're actualy executing the command.



