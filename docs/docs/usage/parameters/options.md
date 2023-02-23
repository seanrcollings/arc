An *arc* option is a (usually optional) parameter that is referenced by name on the command line.

We can take the example from the [previous page](./arguments.md) and convert both of the arguments to options by only adding 2 characters:
```py title="examples/parameter_option.py"
--8<-- "examples/parameter_option.py"
```

Now we can run it, but we must reference each argument by name (prefixed with `--`)
```console
--8<-- "examples/outputs/parameter_option"
```

Notice the difference? We've added a `*,` to the start of the argument list. In Python, any argument that comes after a bare `*` is a [keyword-only argument](https://www.python.org/dev/peps/pep-3102/). In *arc*, this indicates that
the arguments are **options**.


## Documentation
```console
--8<-- "examples/outputs/parameter_option_help"
```
!!! Note
    `lastname` appears before `firstname` in the USAGE because *arc* sorts optionals first

## Alternative Syntax
Like [arguments](./arguments.md#alternative-syntax), options also have an alternative syntax.

Taking the function definition above:
```py
def hello(*, firstname: str, lastname: str | None):
```
We could also have written it as:
```py
def hello(
    firstname: str = arc.Option(),
    lastname: str | None = arc.Option()
):
```
Note that the base `*` is no longer present. When `#!python arc.Option()` is present, it is no longer required because you are explictly telling *arc* what kind of parameter it is. However, it is still allowed.

[Check the reference for a full rundown of the capabilities](../../reference/define/param/constructors.md#arc.define.param.constructors.Option)
