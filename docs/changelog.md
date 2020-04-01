# ARC - A Regular CLI: Change Log
Check out the most recent, and all, versions of Arc.
- [ARC - A Regular CLI: Change Log](#arc---a-regular-cli-change-log)
- [V0.8.3 (No args and anonymous scrips)](#v083-no-args-and-anonymous-scrips)
- [v0.8 (Holy features Batman!)](#v08-holy-features-batman)
- [v0.7 (Configuration)](#v07-configuration)
- [v0.6 (Script Class)](#v06-script-class)
- [v0.5 (???)](#v05)
- [v0.4 (Converters)](#v04-converters)
- [v0.1 - 0.3](#v01---03)

# V0.8.3 (No args and anonymous scrips)
- Implemented No arg scripts
- Implemented anonymous scripts
- Abstracted timer to decorator, so it can be used to test the speed of any function
- Fixed the mess that is the logger

# v0.8 (Holy features Batman!)
- Implemented interactive mode (`-i`)
- Expanded script options to be their own class
- Implemented boolean [flags](options_and_flags.md#flags)
- Rethought how to manage args and kwargs (pass_args, pass_kwargs)
- added tests for examples, builtin utilities, and the script class

# v0.7 (Configuration)
- Rethink of the Config design. Now works soleyly as a module
- Introduced the .arc file for setting loading

# v0.6 (Script Class)
- Major refactor for scripts to be instances of a Script class rather than have all the data in one dictionary
- CLI refactored accordingly to handle this changed

# v0.5 (???)
- I honestly think I messed up the tags on this one since 0.4 and 0.5 are right next to each other

# v0.4 (Converters)
- Implemented Type converters
- Huge amount of documentation added
- Various cleanups
- Added Tests

# v0.1 - 0.3
Intial terrible design for the CLI used in one of my work projects (not even worth talking about honestly)

