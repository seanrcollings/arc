While generally, input is parsed from the command line, there are a few other sources that can be used to provide input.

The precedence of sources is:

1. Commane Line
2. Environment Variables
3. Input Prompt
4. Default Value

!!! note "Type Conversion"
    All input sources, except for default value, will still pass through the type
    conversion systems that *arc* provides.

### Environment Variables
```py title="examples/from_env.py"
--8<-- "examples/from_env.py"
```
Now, if the argument isn't present ont he command line, it will be parsed from the environment variable `VAL`
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