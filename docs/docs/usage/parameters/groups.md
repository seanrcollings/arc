Parameter groups allow you to (as the name implies!) *group* parameters into re-usable chunks. A parameter group can then be used for multiple commands, and each of those commands will have all of those params defined.

## Creating A group
Parameter groups are fairly simple to create, you just need to decorate a class with the `#!python @arc.group` decorator.

```py
@arc.group
class MyGroup:
    ...
```

## Adding Parameters to a group
Now, to make a group *useful*, we need to actually add parameters to it. To do so, we add class-variables with our desired parameter definitions.

For example, let's take this example from the [flags](../flags) page:
```py title="examples/parameter_flag.py"
--8<-- "examples/parameter_flag.py"
```

and convert it to use a parameter group instead.

For this example, the transfer is very straight forward, we can just take the argument list definition, and add it to the class body:

```py
@arc.group
class MyGroup:
    firstname: str
    reverse: bool
```

## Using a group

To use a Parameter Group, all we need to do is add an argument to the argument list of a command, with the
param group as the type hint.

```py
def hello(group: MyGroup): # Don't need firstname or reverse here anymore
```

## Putting it together
```py title="examples/group.py"
--8<-- "examples/group.py"
```

```console
--8<-- "examples/outputs/group"
```

And just like that, we have a set of re-usable parameters that we can add to any command at-will!

## Notes
- Anything that works for regular parameters also works for Parameter groups. This means that `#!python arc.Argument()` and it's cohorts can be used to expand the use of a parameter in a group.
- Because there is no bare `*` or equivelant, there isn't a good way to distinguish between arguments and options. So, any non-flag will be presumed to be an argument unless given an explicit `#!python arc.Option()` as a default value.
- Groups are not permitted to have a default value assigned to them
    ```py
    def hello(group: MyGroup = ...): # This isn't allowed
    ```
- Groups are allowed to be nested arbitrarily
