
*arc* support dynamic loading of subcommands via the `#!python Command.autoload()` method.

This allows you to offer your users to option to extend the functionality of your CLI with their
own custom commands.

`#!python Command.autoload()` can accept an arbitrary number of paths to either files or directories. When given a file, it will attempt to load commands from that file. When given a directory, it will attempt to load every file in that directory. In both cases, if no command is found, it will continue onto the next path rather than erroring.



## Example

=== "timers.py"

    ```py
    # /home/user/timers.py
    import arc

    @arc.command
    def autoload_demo():
        arc.print("I've been autoloaded!")
    ```

=== "cli.py"

    ```py
    # cli.py
    import arc

    @arc.command
    def command():
        ...

    command.autoload("/home/users/timers.py")
    command()
    ```

Now we can run the `autoload-demo` command, without importing it directly
```console
$ python cli.py autoload-demo
I've been autoladed!
```

## Overwriting Commands
By default, commands that are autloaded can overwrite regular commands.


=== "timers.py"

    ```py
    # /home/user/timers.py
    import arc

    @arc.command
    def sub():
        arc.print("I've been autoloaded!")
    ```

=== "cli.py"

    ```py
    # cli.py
    import arc

    @arc.command
    def command():
        ...

    @command.subcommand
    def sub():
        arc.print("I'm the original")

    command.autoload("/home/users/timers.py")
    command()
    ```

```console
$ python cli.py sub
I've been autoladed!
```

You can disable this with a [configuration option](../reference/config.md#configure)
```py
arc.configure(autoload_overwrite=False)
```
