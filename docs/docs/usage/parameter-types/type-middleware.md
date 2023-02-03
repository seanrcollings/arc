Type Niddleware are a powerful tool in *arc* to take control of the value of parameters and do what you need to with them.

## What is a Type Middleware?
A Type Middleware is simply a callable object that recieves a value, and then returns a value of the same
type. It can be used to modify that value, validate some property of that value, or simply analyze the value and return it.

Middlewares fall into a couple of rough categories, and so *arc* uses specific terms to refer to them.

- **Validator**: A middleware that checks the value against some condition. It raises an exception if the condition is not met, and otherwise it returns the original value
- **Transform**: A middleware that modifies the value and returns it.
- **Middleware**: Anything that does not fall into the two above categories

These terms will be used throughout the rest of this page.

## Creating a Type Middleware
Because middleware are *just* callables, they are extremely simple to define.
For example, we could create a transform middleware that rounds floats to 2 digits.

```py
def round2(val: float):
    return round(val, 2)
```

???+ tip
    *arc* already ships with a [`Round()`](../reference/types/transforms.md#arc.types.transforms.numbers.Round)
    middleware, so you wouldn't actually need to implement this one yourself.

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

- [Validators](../reference/types/validators.md)
- [Transforms](../reference/types/transforms.md)