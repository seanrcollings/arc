## Printing
*arc* exports several functions to be used when printing things to the screen:

- `#!python arc.print()` - Wrapper around the normal print function that is aware of whether or not stdout is the terminal or not. If it not a terminal, all escape codes will be removed.
- `#!python arc.info()` - Wrapper around `#!python arc.print()`, but writes to stderr instead of stdout. Useful for quick logging purposes
- `#!python arc.err()` - Wrapper around `#!python arc.print()`, but writes to stderr instead of stdout and styled as an error.

[Reference](../../reference/present/out.md)

## Logging
*arc* has a logger setup that will change it's level based on the current enviroment.

```py
import arc

# Uncomment the below line for the log to
# print to the screen.
# arc.configure(enviroment="development")

@arc.command
def command(ctx: Context):
    ctx.logger.info('hello there!')

command()
```

The levels are:

- development: `INFO`
- production: `WARNING`

You can also set the level to `DEBUG` by setting `#!python arc.configure(debug=True)`, which takes priority over the enviroment.



