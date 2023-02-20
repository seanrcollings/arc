In *arc*, command-line parameters are defined using Python function arguments. This sub-section of the documentation is dedicated to talking about all the components of command line arguments in *arc*.

## Kinds of Parameters
There are several kinds of parameters that *arc* allows you the define. Each of them have their own page that goes into detail on their usage, but here's a quick rundown

- [Arguments](./arguments.md) are provided on the command line positionally. For example the filenames in `grep filename1 filename2` would be *arc* arguments.
- [Options](./arguments.md) are (generally optional, hence the name) parameters that are provided on the command line by-name. For example, in `grep --file <FILENAME>`, `file` would be an *arc* option
- [Flags](./arguments.md) indicate a boolean value. For example, in `grep --invert-match`, `--invert-match` could be represented as an *arc* flag.
- [Counters](./counter.md) are flags that instead of keeping track of whether or not they've been provided, they keep track of the number of times they've been provided

## Parameter Sources
The value for a parameter can come from multiple different sources, if no value is found in the input, these places can be checked:

- Enviorment Variables
- Input Prompt
- Getter Function
- Defalt Values

[For more info](./sources.md)

## Parameter Types
*arc* uses type hints types for type validation / conversion. [See more here](./types/types-intro.md)
