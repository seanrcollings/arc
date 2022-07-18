
*arc* support dynamic loading of subcommands via the `#!python CLI.autoload()` method.

## Example

=== "timers.py"

    ```py
    # /home/user/timers.py
    from arc import namespace

    timers = namespace("timers")

    @timers.subcommand()
    def test():
        arc.print("I've been autoloaded!")
    ```

=== "cli.py"

    ```py
    # cli.py
    from arc import CLI

    cli = CLI()
    cli.autoload("/home/users/timers.py")

    cli()
    ```

Now we can run the `timers:test` command, without importing it directly
```
$ python cli.py timers:test
I've been autoladed!
```

`#!python CLI.autoload()` can accept an arbitrary number of paths to either files or directories. When given a file, it will do as above. When given a directory, it will attempt to load every file in that directory. In both cases, if no command is found, it will continue onto the next path rather than erroring.

!!! warning
    Autoloaded Commands cannot overide commands installed by normal means. This is to prevent a user from accidentally overwriting a part of a tool they where unaware of with their own code.


