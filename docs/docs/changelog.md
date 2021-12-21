
Check out the most recent, and all, versions of Arc.

## `v6.0.0`
- Reworked Type system
- Callbacks like `open_file` and `in_range` are now replaced with type alternatives
- Class-based syntax
- Changed up Customization Interface

## `v5.0.0`
- Is CRAP (don't use)

## `v4.0.0`
- Removed `arc.convert`
- Moved conversion functionality into the `arc.types` package
- Removed `File`, `Range`, `ValidPath`, use their callback counterparts instead
- Changed `arg_aliases` to `short_args` and only allow single-character entries
- Fish autcompletions reimplemented
- Help documentation Arguments section parsing
- Added `stdin` and `stderr` callbacks
- Made the `StandardParser` the default parser

## `v3.3.0`
- StandardParser now accepts **kwargs
- When a command or argument is not valid, arc can now perform a quick check to see if it's likely a misspelling, then suggest the alternative. This can be toggled on and off in the configuration.
- Renamed `@cli.base` to `@cli.default`, removed `Command.base`
- Added `@command` decorator
- Fixed bug that caused `@cli.default` to not check args properly
- added `color.colorize()`

## `v3.2.0`
- Added Standard Parsing Method (`--name value --other-name value2`)
- Added back Raw parser
- Improved generation of usage docs

## `v3.1.0`
- Improved Formatting for `help` command

## `v3.0.1`
- Changes the way that arc handles logging

## `v3.0.0`
- Major improvements / house-cleaning of most of the infrastructure
- CommandType has been renamted to ParsingMethod
- Implemented callback system
- Simplified the Configuration object
- Implemented command aliases and argument aliases
- added `arc` executable
- Tests written using `pytest`
- API Docs!
- More data types are available

## `v2.4.0`
- Fixed bug where a the list converter could not accept only a single item
- Moved the internals for locating the command to excute, and printing out the help information
- Added Command Aliases
- Added `arc.prompt`

## `v2.3.0`
- Can modify the behavior of the tool when no command is provided with `@cli.base`
- Multiple Commands can be installed for the same function

## `v2.2.0`
- Adds autocompletion support for the fish shell
- Adds Command autoloading support
- Beefed up the Config
  - Config is internally more rigidly defined
  - Exposes it's functionality for making tool-related config objects
- Fixed issue with emojis not being parsed properly (probably happened with other Unicode characters too)
- `fg.hex` and `bg.hex`
- Improves error handling for type conversion errors
- Adds the `presenter` package. Still in dev, so documentation non-existant currently

## `v2.1.0`
- Context can now be subclassed for typing and extra functionality
- Arc support kebab-case on the command line

## `v2.0.2`
- Calling `Command#base` now internal data based on the new function provided

## `v2.0.1`
- Fixed an issue where installing subcommands into a namespace, then installing that namespace into parent would cause the context to not propagate properly.
- Added `Command#install_commands` as a wrapper around `Command#install_command` for installing multiple commands at once. Returns a tuple containing all the command objects

## `v2.0` (Big Changes)
- Renamed scripts to comands
- Ditched the Concept of scripts and script containers. Commands contain their own subcommands
- Commands can be arbitrarily nested
- added `namespace` function for creating a subcommand not attached to the CLI
- Got rid of the Utility class (use `namespace`) instead
- Added `context`
- Improved parser
- Tons of general code improvement


## `v1.2.1`
- Fixed a bug with the `SelectionMenu` UI where state from a previous class instance would persist into a new class instance

## `v1.2`
- Improved Error handling
  - replaced `debug` and `log` config options with a single `loglevel` that expects one of the standard python loglevels (`loggin.DEBUG`, `logging.WARNING` etc...)
  - When `loglevel` is not set explictly, it is set to `logging.WARNGING`. All exceptions will just log the error message. When set to debug, tracebacks will be logged along with error messages
- Added UI package and a basic `SelectionMenu` class. Check [here](./ui.md) for details.
- Modified the `color` module
  - Removed the `background` method on foreground colors. Now bacground colors are only available through the `bg` class
  - added an `rgb` function to both `fg` and `bg` which take in values for Red, Green, and Blue in range [0, 255]


## `v1.1`
- Added File type
- General code improvements

## `v1.0` (First Major Version!)
- Implmented different [ScriptTypes](./scripts/script_types.md) that interpret input differently
- Added supprot for Type Alias conversions, like `List[int]` currently only supports Union, List, Set, and Tuple Alias
- Quoted options (option_name="option with spaces") function properly again
- Parser now enables the use of anon scripts
- Arc no longer errors when a .arc file is not present (whoops)
- Users can now implement a custom script class to handle user input

## `v0.9`![alt](https://link) (Improved Parsing)
- Implemented a parsing engine for the user input
- Removed no_args special script (can just use a anon script with no args)
- Input functions for each converter (convert_to_<converter_name>)
- Removed `pass_args` and `pass_kwargs`
- Added `convert` paramater to scripts

## `v0.8.3` (No args and anonymous scrips)
- Implemented No arg scripts
- Implemented anonymous scripts
- Abstracted timer to decorator, so it can be used to test the speed of any function
- Fixed the mess that is the logger

## `v0.8` (Holy features Batman!)
- Implemented interactive mode (`-i`)
- Expanded script options to be their own class
- Implemented boolean [flags](options_and_flags.md#flags)
- Rethought how to manage args and kwargs (pass_args, pass_kwargs)
- added tests for examples, builtin utilities, and the script class

## `v0.7` (Configuration)
- Rethink of the Config design. Now works soleyly as a module
- Introduced the .arc file for setting loading

## `v0.6` (Script Class)
- Major refactor for scripts to be instances of a Script class rather than have all the data in one dictionary
- CLI refactored accordingly to handle this changed

## `v0.5` (???)
- I honestly think I messed up the tags on this one since 0.4 and 0.5 are right next to each other

## `v0.4` (Converters)
- Implemented Type converters
- Huge amount of documentation added
- Various cleanups
- Added Tests

## `v0.1 - 0.3`
Intial terrible design for the CLI used in one of my work projects (not even worth talking about honestly)

