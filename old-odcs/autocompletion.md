# Command Autocompletion
**Note: Currently only the Fish shell has supported autocompletions. Support for zsh and bash will be coming soon.**

Any CLI worth its salt should come packed with autocompletions for popular shells. Luckily, ARC can generate autocompletion data for you, so you don't even have to worry about it! To enable autcompletion for your CLI, all you need to do is

```py
from arc import CLI

cli = CLI("toolname")
# You'll want to provide the tool name in the CLI initialization, so it knows what to provide completions for on the command line. Otherwise, it'll just default to 'cli'
cli.autocomplete()
```

Now with autcompletion enabled for your tool, a user needs only to add this line to their shell config
```
toolname _autocomplete:init <SHELL NAME> | source
```

Voila! Just like that and you tool is providing autocompletions!