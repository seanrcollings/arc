An *arc* argument is a parameter which get passed to the command **positionally**. They are defined using regular Python function arguments.

```py
--8<-- "examples/parameter_argument.py"
```
Notice that we annotated the first argument as `#!python str`, but the second argument as `#!python str | None`? We do this because we want `firstname` to be **required** and `lastname` to be **optional**. By giving `lastname` a union type that includes `None`, we're letting *arc* know that if no value is passed in from the command line, it's ok for it to be `#!python None`.

??? info "Using None"
    In *arc*, defining parameters as allowing `#!python None`, can be done in several ways, all of which are equivelant. The following are all equivelant:
    ```py
    def hello(firstname: str, lastname: str | None):
    ```
    Setting it explictly
    ```py
    def hello(firstname: str, lastname: str | None = None):
    ```
    If you set the default as `None`, you don't actually have to annotate as such if not desired
    ```py
    def hello(firstname: str, lastname: str = None):
    ```


We can see it in action here
```console
--8<-- "examples/outputs/parameter_argument"
```

And adding the optional `lastname`
```console
--8<-- "examples/outputs/parameter_argument_lastname"
```

## Documentation
```console
--8<-- "examples/outputs/parameter_argument_help"
```
!!! Note
    The brackets around `lastname` in the USAGE indicate that it is optional


## Default Values
Often, we don't just want a `None` when a value isn't provided, but we want some sort of default. This can be accomplished by simply giving the argument a default value.

```py title="examples/parameter_default.py"
--8<-- "examples/parameter_default.py"
```
Note the lack of `None` in the type signature. Now that we have a default, the value will *always* be a string, and we don't need to tell *arc* that the value is optional.

Check it:
```console
--8<-- "examples/outputs/parameter_default"
```

## Alternative Syntax
*arc* has an alternative syntax fo defining arguments

Take this argument from the last example
```py
lastname: str = "Joestar"
```

Could also be defined as:
```py
lastname: str = arc.Argument(default="Joestar")
```

Now, `arc.Argument` is unnecessary here, but comes with some additional bells and whistles that make it more useful. Some of these features will be explored in future guides, or you [check the reference for full details on what it provides](../../reference/define/param/constructors.md#arc.define.param.constructors.Argument).
