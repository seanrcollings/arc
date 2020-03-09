# Args and kwargs
When creating a script, there are two other options that we haven't talked about `pass_args` and `pass_kwargs`. These allow you to tell the script to not try and compare the user's input to your options, but simply pass them as positional arguments or keyword arguments. While I would generaly recommend against this approach, there are certain times you need to.

## pass_args
By instucting Arc to simply pass all args entered by the user to the script, you get complete control over handling the user's arguments.
```py
@cli.script("print_args", pass_args=True)
def print_args(*args):
    print(*args)
```
```
$ python3 example.py print_args here are all my args that I am passing to the script
here are all my args that I am passing to the script
$
```

## pass_kwargs
By instucting Arc to simply pass all arguments as keywords, you can have Arc do a little bit of parsing, but still not work about checking if it's one of your options
```py
@cli.script("print_kwargs", pass_kwargs=True)
def print_kwargs(**kwargs):
    for key, value in kwargs:
        print(f"{key} : {value}")
```
```
$ python3 example.py print_kwargs key1=value1 key2=value2 key3=value3
key1: value1
key2: value2
key3: value3
$
```

Keep in mind that if you do set pass_args or pass_kwargs to True, you **cannot** provide any options to your script
However, you can still define flags
```py
@cli.script("print_args", flags=["--greet"], pass_args=True)
def print_args(*args, greet):
    if greet:
        print("Hello!")
    print(*args)
```
```
$ python3 example.py print_args here are all my args that I am passing to the script --greet
"Hello!"
here are all my args that I am passing to the script
$
```



