# Scripts
Arc Scripts come several different flavors. Each flavor changes the way that input is interpreted and how
it will be passed to the users's function.

These are as follows:
- Keyword
- Positional
- Legacy
- Raw

Details on each can be seen [here](./script_types.md)

## Script type is inherited
Script types can be specified on the CLI, Utility, or Script level.
```py
from arc import CLI
from arc import ScriptType as st

cli = CLI(script_type=st.KEYWORD) # At CLI level

util = Utility("name", script_type=st.POSITIONAL) # at Utility level

@cli.script("greeting", st.RAW)  # At Script level
#....
```
If the script type is not defined on the script, it inherits the type of it's Parent container (Either the cli or a utility). In the case of a utility, if it also not defined, it inherits from the CLI which by default is `KEYWORKD`

## [Custom Scripts](./custom_script_type.md)

