## `6.4.0`
- [Shell Completions](./usage/shell-completions.md) now enabled with `arc.configure()`
- Callbacks are no longer required to `yield` to be valid
- Improved some error messages
- Fixed a bug to do with callback error handling
- Added [error handlers](./usage/error-handlers.md) as syntatic sugar for callback error handling
- Add `User` and `Group` type

## `6.3.0`

- Added the ability to gather input from environment variables or by prompting the user directly.
- Added `prompt.select()` for a more elegant selection menu
- Implemented [Shell Completions](./usage/shell-completions.md) for Bash, Zsh, and Fish. **CURRENTLY EXPERIMENTAL**
- Fixed bug where specifying the `version` for the CLI would cause the application to crash

## `6.2.2`

- Fixed bug with `IoWrapper`

## `6.2.1`

- Fixed command debug utilites


## `6.2.0`

- Added [global cli options](./usage/cli.md#global-options)
- Changed the implementation for gathering `State` so now it's consistent across commands, `cli.options` and callbacks

## `6.1.0`

- Added [command callbacks](./usage/callbacks.md)

## `6.0.1`

- `typing.Optional[T]` and default value of `None` now work identically, and have the expected behavior.

## `6.0.0`
First Version where I decided to keep better track of changes version-to-version. So there's no history before this :(