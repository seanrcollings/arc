
Plugins are a way for third party packages to extend the functionality of *arc*.
They can be either be added by the user or by the developer of the CLI application,
depending on how the plugin loading has been configured.

Generally, plugins look like the following:

```py title="examples/plugin.py"
--8<-- "examples/plugin.py"
```

The plugin is a callable that receives the `#!python arc.Context()` object as its only argument.
This function can then be used to add new commands, options, arguments, middlewares, etc. to the CLI application.


## Loading Plugins
Plugins are loaded in three ways:

1. By Path
2. By Entrypoint Group
3. By Entrypoint Value

=== "By Path"
    Paths should be a list of strings that point to either a python file or a directory.
    If a directory is provided, all python files in that directory will
    attempted be loaded as plugins.

    Each plugin that is to be loaded should have a callable object named `plugin` that takes a single argument, the `#!python arc.Context()` object.

    ```py
    import arc

    arc.configure(
        plugin=arc.PluginConfig(
            paths=[
                "/path/to/plugin.py",
                "/path/to/other/plugin.py",
                "/path/to/another/directory/",
            ]
        )
    )
    ```

=== "By Entrypoint Group"
    A list of entry points groups as defined by the [Entry Point Specification](https://packaging.python.org/en/latest/specifications/entry-points/). The value of the entrypoint should be a callable object that takes a single argument, the `#!python arc.Context()` object.

    ```py
    import arc

    arc.configure(
        plugin=arc.PluginConfig(
            groups=[
                "arc.plugins",
                "myapp.plugins",
            ]
        )
    )
    ```

=== "By Entrypoint Value"

    A list of entry points values as defined by the [Entry Point Specification](https://packaging.python.org/en/latest/specifications/entry-points/). Should be a callable object that takes a single argument, the `#!python arc.Context()` object.

    ```py
    import arc

    arc.configure(
        plugin=arc.PluginConfig(
            entrypoints=[
                "myapp:plugin.plugin",
                "myapp:plugin.other_plugin",
            ]
        )
    )
    ```
