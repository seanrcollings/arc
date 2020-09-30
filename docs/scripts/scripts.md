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
```py x
from arc import CLI, Utility, ScriptType as st

cli = CLI(script_type=st.KEYWORD) # At CLI level

util = Utility("name", script_type=st.POSITIONAL) # at Utility level

@cli.script("greeting", st.RAW)  # At Script level
def greeting(*args):
    print(args)
```
If the script type is not defined on the script, it inherits the type of it's Parent container (Either the cli or a utility). In the case of a utility, if it also not defined, it inherits from the CLI which by default is `KEYWORKD`. 
Keep in mind that when it comes to utilites, they must be registered to the CLI before registering any scripts to them if you want those scripts to inherit the `script_type` of the CLI.
### This Works:
```py x
from arc import CLI, Utility, ScriptType as st

util = Utility("name")
cli = CLI(utilities=[util], script_type=st.POSITIONAL) 
# since util doesn't specify a script type, 
# when it's registered it inherits it form the CLI

@util.script("greeting") # This script's script type would also be Positional
def greeting(*args):
    print(args)

```

### This Does not:
```py x
from arc import CLI, Utility, ScriptType as st

util = Utility("name") # util is created with Default script type

@util.script("greeting") # This script is created with the util's script type
def greeting(**kwargs):
    print(args)

cli = CLI(utilities=[util], script_type=st.POSITIONAL) 
# Util's script type is changed, but the 'greeting' script would not be
# If other util scripts are defined below this point, they will recieve
# the POSITIONAL script type
```
To avoid this issue, it is generally best practice to define all your utilities, then register them the cli, then define the scripts
```py
from arc import CLI, Utility, ScriptType as st

util = Utility("name")
util2 = Utility("name2")
util3 = Utility("name3")
cli = CLI(utilities=[util, util2, util3], script_type=st.POSITIONAL)
# all would recieve the POSITIONAL script type

@util.script("greeting") # This script's script type would be Positional
def greeting(*args):
    print(args)

```
For Utilities split between multiple files, explictly defining their script type would be better.

## [Custom Scripts](./custom_script_type.md)    

