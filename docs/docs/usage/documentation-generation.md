Every *arc* application / command comes with a builtin `--help` flag.

## Example
```py title="hello.py"
--8<-- "examples/hello.py"
```
```console
--8<-- "examples/outputs/hello_help"
```

## Docstrings as documentation
As seen above, *arc* uses function docstrings as a source for documentation. Arc understands the following format for docstrings:
```py
def func():
    """[description]

    # <section-name>
    section body

    with paragraphs!

    # <second-section-name>
    ...
    """
```

For example, given the following:
```py title="docstring_example.py"
--8<-- "examples/docstring_example.py"
```
arc will format it as follows:
```console
--8<-- "examples/outputs/docstring_example"
```

## Paramater Documentation
Command parameters may be documented in two ways.

1. Using the `description` argument of `Argument` / `Option` / `Flag` / `Param`. This option takes precedence if both are present.
2. Adding an `# Arguments` section to the docstring with the correct formatting.

For example these two commands:
```py title="arguments_documentation.py"
--8<-- "examples/arguments_documentation.py"
```
Will produce near-identical output:
```console
--8<-- "examples/outputs/arguments_documentation"
```

Which to use is really up to personal preference, however I prefer to place documentation in the docstring because I think it cleans up the function definition.
