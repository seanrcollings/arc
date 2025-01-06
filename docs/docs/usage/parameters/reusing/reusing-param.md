# Reusing Params

As your CLI grows, you may find that you have a lot of commands that share the similar parameters. To help with that, `arc` provides a couple of different ways to reuse parameters.


## Type Annotation

The reccomended way to reuse paramters is to bind your Param defintion to a type annotation

```py title="examples/type_annotation_param.py"
--8<-- "examples/type_annotation_param.py"
```

```console
--8<-- "examples/outputs/type_annotation_param"
```

Now anywhere you use this `ConfigPathParam` type, the CLI will will have the same param.


## Using a group

To use a Parameter Group, all we need to do is add an argument to the argument list of a command, with the

param group as the type hint.

```py title="examples/group.py"
--8<-- "examples/group.py"
```

```console
--8<-- "examples/outputs/group"
```

Reference [Parameter Groups](/usage/parameters/reusing/groups/) for more information.
