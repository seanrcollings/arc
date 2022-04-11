!!! warning
    Shell completions are currently an
    **experimental** feature. There is no guarantee that they will work or if
    the API for using them will be stable. As such, the feature is disabled by default
    To enable shell completions, add the following to your script:

    ```py
    cli.autocomplete()
    ```

The autocompletions will be generated with the following
commands for shell. `foo` is used as an example command entry point / name
=== "bash"
    Add two `~/.bashrc`
    ```bash
    eval "$(foo --autocomplete bash)"
    ```
=== "zhs"
    Add to `~/.zshrc`
    ```zsh
    eval "$(foo --autocomplete zsh)"
    ```
=== "fish"
    Add to `~/.config/fish/config.fish`
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

## Custom Completions
