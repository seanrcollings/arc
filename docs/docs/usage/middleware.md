*arc* is based on a middleware design pattern. In arc there are three kinds:

- **Initialization middlewares** - Middleware that run a single time on startup. These are expected to perform the necessary setup to get an *arc* application up and running. The default middleware stack does, among other things, the following:
    - Performs development mode checks
    - Normalizes the differences between input sources
    - Validates that input
    - Parses the input from the command line
    - Prepares the context object for execution
- **Execution Middlewares** - Middleware that run every-time a command is executed. Each command will have associated middlewares and when a command is chosen all of it's parents middlewares will be ran, then it's middlewares, then the callback. The default middleware stack does, among other things, the following:
    - Associates parsed values with command parameters
    - Retrieves values from other parameter sources (enviroment variables, user input, etc...)
    - Performs type conversion on parsed values
    - Executes validations on parsed values (ensures that they meet the requirements of the parameter)
- **Type Middlewares** - [Middlewares that operate on the type level](./parameters/types/type-middleware.md). These middlewares are unique and will not be covered on this page. But they are used to add validations / transformations to a type.


## Middleware Example
A middleware is a callable object that receives and instance of `#!python arc.Context`, which serves as a dict-like object that all middleware share. Each middleware can then perform manipulations to this context object to get their desired effect.

In this example, we add a middleware that simple prints out some information about the command that is about to be executed.

```py title="examples/middleware/middleware.py"
--8<-- "examples/middleware/middleware.py"
```

```console
--8<-- "examples/outputs/middleware/middleware"
```


## Registering Middlewares
Custom middleware can be added using the `#!python @object.use` interface

### Init Middleware
The add init middlewares to your application, you are required to construct the `App` object explicitly
```py
@arc.command
def command():
   ...

app = arc.App(command)

@app.use
def middleware(ctx):
    ...

app()
```
### Exec Middleware
Execution middlewares are registered with commands specifically.

```py
@arc.command
def command():
   ...

@command.use
def middleware(ctx):
    ...
```

## Suspending Execution
Middlewares may suspend their execution, and resume it after the command has executed by yielding.
```py
def middleware(ctx: Context):
	# Perform setup logic
	res = yield
	# Perform teardown logic
```

The generators will be resumed in reverse order after command execution. The generator will be `sent()` the returned result of the command (or previous middleware). You may then choose to return something else which will be used as the result sent to the next middleware.

## Replace Context
If you'd like to completely replace the context object, you may do so by returning (or yielding) a different object from your middleware.

```py
def middleware(ctx: Context):
	return {"arc.args": {...}}

# OR

def middleware(ctx: Context):
	yield {"arc.args": {...}}
```

## Halting Execution
Stopping the rest of the pipeline from running should be accomplished by raising an exception
```py
def middleware(ctx: Context):
	arc.exit(1, "Something bad occured") # raises a SystemExit
	# OR
	raise arc.ExecutionError("Something bad occured") # If you want an exception that other middlewares can catch
	# OR
	raise CustomException(...)
```

## Catching Exceptions
Middlewares are capable of catching exceptions that occur further down the pipeline by yielding inside of a try-except block:
```py
def middleware(ctx: Context):
    try:
        yield
    except Exception:
        # Handle the exception, or raise again
```


If the handler can't handle a particular error, you can `raise` the exception again (or even raise a new exception). This will cause it to continue down the list of middlewares until it finds one that does handle the exception. If none are found, the exception will be handled by *arc's* default error-handling behavior.

??? TIP "Alternative Error Handler Syntax"
    Because error handling in middlewares is a common pattern, *arc* supports
    an alternate syntax for defining them.
    ```py title="examples/errors/error_handlers.py"
    --8<-- "examples/errors/error_handlers.py"
    ```

    ```console
    --8<-- "examples/outputs/errors/error_handlers"
    ```
    See [Error Handling](./error-handlers.md) for more information


## Modifying the Middleware Stack
By default `#!python use()` adds the provided middleware to the end of the stack. Instead, you can provide various arguments to place it in a specific location

```py
command.use(mid1, pos=4) # at index 4
command.use(mid2, after=mid1) # Inserted directly after mid1
command.use(mid3, before=mid1) # Inserted directly before mid1
command.use(mid4, replace=mid2) # Replaces mid2 with mid1
```

This can be used to override the default behavior of *arc*. For example, this could be used to replace arc's parsing middleware with your own.


```py
import arc

@arc.command
def command():
    ...


app = arc.App()

@app.use(replace=arc.InitMiddleware.Parser)
def parsing(ctx):
    # Do custom parsing

app()
```

Be careful when replacing middlewares, as it may break the functionality of *arc*. Most middlewares expect certain data to be in the Context object and will fail if it is not present. For example, if you replace the `#!python arc.InitMiddleware.Parser` middleware, you will need to ensure that the `arc.parser.result` key is present in the context object and contains the parsed arguments.

You can review the reference for both the [init middlewares](../reference/runtime/init.md) and [execution middlewares](../reference/runtime/exec.md) to see what data they expect to be present in and what data they add to the context object.
