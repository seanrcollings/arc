*arc* comes with tooling for requsting input from the user in the form of the `arc.prompt` package. Here's a quick example of it in action:
```py title="examples/user_input.py"
--8<-- "examples/user_input.py"
```

```console
$ python user_input.py
Name: Sean
Are you sure? [y/n] y
Hello, Sean!
```

## Writing a Question
Below is an example of how you could write a custom `RegexQuesion` that validates user input to match a provided regular expression
```py title="examples/custom_question.py"
--8<-- "examples/custom_question.py"
```

```console
$ python custom_question.py
Pick a number [Must match: '\d+'] 2
You picked: 2
```

You can look at the [reference](../reference/prompt/questions.md) to see the kinds of questions that *arc* ships with by default.

## Configuring the Prompt

You can provide your own Prompt instance like so:
```py
import arc
from arc.prompt import Prompt

arc.configure(prompt=Prompt()) # could also be a subclass, etc...
```

!!! tip
    The prompt object you recieve via [dependency injection](./parameters/dependancy-injection.md) is the same object that powers the [`prompt` functionality of parameters](./parameters/sources.md#input-prompt). By configuring your own customized instance of the prompt, you can have the same appearance across both uses.
