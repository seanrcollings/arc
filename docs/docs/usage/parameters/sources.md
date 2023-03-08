While generally, input is parsed from the command line, there are a few other sources that parameters can recieve values from

The precedence of sources is:

1. Command Line
2. Environment Variables
3. Input Prompt
4. Getter Function
5. Default Value

!!! note "Type Conversion"
    All input sources, except for default value, will still pass through the type
    conversion systems that *arc* provides. If the value you return for something
    is already the correct type, it will be passed over.

### Command Line
When an *arc* command is executed it will check `#!python sys.argv` for input. However, you can actually provide explcit input as the first argument to call:

```py title="examples/command_string.py"
--8<-- "examples/command_string.py"
```

```console
--8<-- "examples/outputs/command_string"
```
You generally don't need to do this, but it's useful for when you want to test your interface. (In fact, that's how pretty much all of *arc's* own tests are defined)


### Environment Variables
```py title="examples/from_env.py"
--8<-- "examples/from_env.py"
```
Now, if the argument isn't present on the command line, it will be parsed from the environment variable `VAL`
```console
--8<-- "examples/outputs/from_env"
```

### Input Prompt
If there is no input provided on the command line for `name` (and there was no enviroment variable), *arc* will prompt the user for input.
```py title="examples/from_prompt.py"
--8<-- "examples/from_prompt.py"
```
```console
$ python from_prompt.py Jolyne
Hello, Jolyne

$ python from_prompt.py
What is your name? Jolyne
Hello, Jolyne
```
If the parameter is optional, the user will be still be prompted, but the user can enter an empty input by just pressing *Enter* and the default will be used.

TODO: Customzing the prompt object

### Getter Function
Getter functions are a way to provide a default for an argument, based on the result of a function call.
```py title="examples/from_getter.py"
--8<-- "examples/from_getter.py"
```

```console
--8<-- "examples/outputs/from_getter"
```

#### Different Syntax
Getter functions may also be defined using this decorator syntax
```py title="examples/from_getter_alias.py"
--8<-- "examples/from_getter_alias.py"
```

### Default Value
If none of the above are satisfied first, *arc* will check for a default value of your parameter.

```py title="examples/parameter_default.py"
--8<-- "examples/parameter_default.py"
```

```console
--8<-- "examples/outputs/parameter_default"
```

If there is no default (like with `firstname` above), *arc* will emit an error
```console
--8<-- "examples/outputs/parameter_default_error"
```

## Checking origin of parameter value
You can check what the origin of a value is like this:

```py title="examples/origins.py"
--8<-- "examples/origins.py"
```

```console
--8<-- "examples/outputs/origins"
```
