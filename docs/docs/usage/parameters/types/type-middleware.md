As stated before, *arc* is based on a Middleware design pattern. This also applies to *arc's* type system to give you further flexibility in defining your APIs.

## What is a Type Middleware?
A Type Middleware is simply a callable object that recieves a value, and then returns a value of the same
type. It can be used to modify that value, validate some property of that value, or simply analyze the value and return it.

Middlewares fall into a couple of rough categories, and so *arc* uses specific terms to refer to them.

- **Validator**: A middleware that checks the value against some condition. It raises an exception if the condition is not met, and otherwise it returns the original value
- **Transformer**: A middleware that modifies the value and returns it.
- **Observer**: A middleware that just analyzes the type, but won't every raise an error / manipulate it

These terms will be used throughout the rest of this page.

## Creating a Type Middleware
Because middleware are *just* callables, they are extremely simple to define.
For example, we could create a transform middleware that rounds floats to 2 digits.

```py
def round2(val: float):
    return round(val, 2)
```

???+ tip
    *arc* already ships with a [`Round()`](../../../reference/types/middleware/transformers.md#arc.types.middleware.transformers.Round)
    transformer, so you wouldn't actually need to implement this one yourself.

## Using a Type Middleware

Type Middleware are *attched* to a type using an [Annotated Type](https://docs.python.org/3.9/library/typing.html#typing.Annotated)

```py title="examples/type_middleware_round.py"
--8<-- "examples/type_middleware_round.py"
```

```console
--8<-- "examples/outputs/type_middleware_round"
```

???+ tip
    Middlewares are actually why most custom *arc* types require you to use `#!python arc.convert()` to
    convert them properly. A good majority of them are *actually* just an underlying type + some middleware to provide a validation / conversion step. For example `#!python arc.types.PositiveInt` is actually just defined as
    ```py
    PositiveInt = Annotated[int, GreaterThan(0)]
    ```

## Builtin Middlewares
*arc* ships with a set of general-use builtin middlewares

- [Validators](../../../reference/types/middleware/validators.md)
- [Transformers](../../../reference/types/middleware/transformers.md)
- [Observers](../../../reference/types/middleware/observers.md)

## Examples

Middleware that ensure that a passed in version is greater than the current version

```py title="examples/new_version.py"
--8<-- "examples/new_version.py"
```

```console
--8<-- "examples/outputs/new_version"
```
