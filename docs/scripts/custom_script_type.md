# Custom Script Types
If the builtin script types are not suitable for your needs, Arc provides functionality to provide a custom script type.

## Script API
Custom scripts inherit from Script ([/src/arc/script/script.py](../../src/arc/script/script.py))
### Instance Params
- `name: str` - Name of the script. Either specified in the script decorator or assumed by the function name.
- `function: Callable` - Function that the script binds to.
- `options: List[Option]` - List of option objects that the Script builds on intialization. Should be modified as needed
- `flags: List[Flags]` - List of flag objects that the Script builds on initialization. Should be modified as needed
- `validation_errors: List[str]` - List of messages fontaining info on what went wrong during script building. If it contains any items, the script will not execute
- `doc: str` - Contains the doc-string of the aforementioned function object. If the function does not contain a doc-string, it will default to `No Docsting`

### Methods
#### Abstract Methods
- `execute(self, script_node) -> None` - Called at the end of the execution chain. At this point, the shape of your Option and Flag objects should be completed and ready to be passed into the function. At the end of this method, self.function should be called.

- `match_input(self, script_node) -> None` - called with a [ScriptNode](../../src/arc/parser/data_types.py) object. This method should look at the internals of the ScriptNode object and determine which options in `self.options` and witch flags in `self.flags` match to the user input.

#### Other Methods
- `arg_hook(self, builder) -> None` - Hook to validate each Option and Flag object as they are being created. Is called each time with the current [builder](./arg_builder.md) object.

- `validate_input(self, script_node) -> None` - Hook to validate input before it gets passed to `match_input`. Not strictly needed, but can be useful in pulling some checks out of `match_input` or other input methods. Should raise a `arc.ValidationError` if all checks are not passed.

- `arg_builder(self) -> Tuple[Dict[str, Option], Dict[str, Flag]]` - Handles buildings the Options and Flags objects. Calls `arg_hook` for each argument it parses. Generally, it's implementation + `arg_hook` is enough for most script types and shouldn't need to be overidden.

## Example
Heres a basic example to demonstrate a custom Script implementation
```python
from arc import CLI, ScriptType as st
from arc.script.script import Script


class TestScript(Script):
    def execute(self, script_node):
        print("execute")

    def match_input(self, script_node):
        print("match input")

    def arg_hook(self, builder):
        print("arg hook")

    def validate_input(self, script_node):
        print("valiate input")


st.add_script_type("test", TestScript) # "test".upper() will act as your identifier


cli = CLI()


@cli.script("test", st.TEST)
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
