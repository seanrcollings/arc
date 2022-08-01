`#!python list`

Collection types (`#!python list`, `#!python set`, `#!python tuple`) can be used to gather multiple values into a single parameter.
When used as a positional parameter `#!python list` acts similarly to `#!python *args`
```py title="list_argument.py"
--8<-- "examples/list_argument.py"
```
```console
--8<-- "examples/outputs/list_argument"
```
Because `list` can accept any number of values, you won't be able to add additional arguments after `names`. Any other positional arguments would have to come before `names`.

When used as an option, it allows the option to be used multiple times:
```py title="list_option.py"
--8<-- "examples/list_option.py"
```
```console
--8<-- "examples/outputs/list_option"
```
Collections can be sub-typed so that each item will be converted to the proper type:
```py title="sum.py"
--8<-- "examples/sum.py"
```
```console
--8<-- "examples/outputs/sum"
```

`#!python set`

Similar to `list`, but will filter out any non-unique elements.

```py title="set_argument.py"
--8<-- "examples/set_argument.py"
```
```console
--8<-- "examples/outputs/set_argument"
```

`#!python tuple`

Similar to `list`, but with some additional functionality.

According to PEP 484:

- `#!python tuple` represents an arbitrarily sized tuple of any type. In *arc*, this will behave the same as `#!python list`
- `#!python tuple[int, ...]` represents an arbitrarily sized tuple of integers. In *arc*, this will behave the same as `#!python list[int]`
- `#!python tuple[int, int]` represents a size-two tuple of integers. In *arc*, this behavior is unique to `#!python tuple` as the parameter will only select 2 values from input.

`#!python dict`

Allows a list of comma-seperated key-value pairs. Can be typed generically on both keys and values.
```py title="dict_argument.py"
--8<-- "examples/dict_argument.py"
```
```console
--8<-- "examples/outputs/dict_argument"
```