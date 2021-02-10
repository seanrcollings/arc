# Custom Command Types
If the builtin command types are not suitable for your needs, Arc provides functionality to provide a custom command type.

# Command
Custom scripts inherit from Command ([/src/arc/command/command.py](../../src/arc/command/command.py))
## Instance Params
- `name: str` - Name of the command. Either specified in the command decorator or assumed by the function name.
- `function: Callable` - Function that the command binds to.
- `args: List[Option]` - List of options object, these will need to be matched up to the user's input
- `validation_errors: List[str]` - List of messages fontaining info on what went wrong during command building. If it contains any items, the command will not execute
- `doc: str` - Contains the doc-string of the aforementioned function object. If the function does not contain a doc-string, it will default to `No Docsting`

## Methods
### Abstract Methods
- ### `execute(self, command_node) -> None`
  **Description:** Called at the end of the execution chain. At this point, the shape of your Option and Flag objects should be completed and ready to be passed into the function. At the end of this method, `self.function` should be called.

  **Arguments**
    - `command_node` : [DEPRECATED] Instance of `CommandNode` from the parser. Defined [here](../../src/arc/parser/data_types.py). Contains the options, flags, and arbitrary arguments that the parser parsed.


- ### `match_input(self, command_node) -> None`
  **Description:** Matches the usere's input with the possbile command arguements

  **Arguments:**
    - `command_node`: Instance of `CommandNode` from the parser. Defined [here](../../src/arc/parser/data_types.py). Contains the options, flags, and arbitrary arguments that the parser parsed.

### Helper Methods
- ### `arg_hook(self, param, meta) -> None`
  **Description:** Hook to validate each Option and Flag object as they are being created. If an error is detected, raise a ScriptError

  **Arguments:**
    - `param` : A paramater object from the [Python inspect library](https://docs.python.org/3/library/inspect.html#inspect.Parameter)
    - `meta` : Dictionary of other data relating to the current paramater. Currently only stores it's position in the argument list, and the length of the arguement list. In the future it may store other data.

- ### `validate_input(self, command_node) -> None`
  **Description:** Hook to validate input before it gets passed to `match_input`. Not strictly needed, but can be useful in pulling some checks out of `match_input` or other input methods. Should raise a `arc.ValidationError` if all checks are not passed.

    **Arguments:**
  - `command_node`: Instance of `CommandNode` from the parser. Defined [here](../../src/arc/parser/data_types.py) Contains the options, flags, and arbitrary arguments that the parser parsed.


- ### `arg_builder(self) -> Tuple[Dict[str, Option], Dict[str, Flag]]`
  **Description:** Handles buildings the Options and Flags objects. Calls `arg_hook` for each argument it parses. Generally, it's implementation + `arg_hook` is enough for most command types and shouldn't need to be overidden.

## Full Example
Heres a basic example to demonstrate a custom Command implementation
```python
from arc import CLI, CommandType as ct
from arc.command.command import Command


class TestCommand(Command):
    def execute(self, command_node):
        print("execute")

    def match_input(self, command_node):
        print("match input")

    def arg_hook(self, builder):
        print("arg hook")

    def validate_input(self, command_node):
        print("valiate input")


ct.add_script_type("test", TestCommand) # "test".upper() will act as your identifier


cli = CLI()


@cli.subcommand(test", ct.TEST)
def test(arg1, arg2):
    pass


cli()
```

```out
$ python3 example.py test
arg hook
arg hook
validate input
match input
execute
```
