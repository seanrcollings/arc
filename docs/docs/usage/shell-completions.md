!!! warning
    Shell completions are currently an
    **experimental** feature. There is no guarantee that they will work or if
    the API for using them will be stable. As such, the feature is disabled by default
    To enable shell completions, add the following to your script:

    ```py
    cli.autocomplete()
    ```

The autocompletions will be generated with the following
commands. `foo` is used as an example command entry point / name
=== "bash"
    Add to `~/.bashrc`
    ```bash
    eval "$(foo --autocomplete bash)"
    ```
=== "zsh"
    Add to `~/.zshrc`
    ```zsh
    eval "$(foo --autocomplete zsh)"
    ```
=== "fish"
    Add to `~/.config/fish/completions/foo.fish`
    ```fish
    foo --autocomplete fish | source
    ```

## Type Completions

Argument types can provide shell completions for the argument.

For example, arc's builtin support for `enum.Enum` provides completions for it's possible options
```py title="examples/paint.py"
--8<-- "examples/paint.py"
```

```console
$ paint <tab>
red yellow green
```

The following types have builtin completion support:

- `#!python enum.Enum`
- `#!python  typing.Literal`
- `#!python  arc.types.ValidPath`
- `#!python  arc.types.FilePath`
- `#!python  arc.types.DirectoryPath`

### Custom Types
When implenting your own types, you can provide completions for them implementing the `#!python __completions__()` method on your class.

```py title="examples/custom_type_completions.py"
--8<-- "examples/custom_type_completions.py"
```

```console
$ custom_type_example <tab>
1 2
```
