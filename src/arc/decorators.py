from functools import wraps


class BaseDecorator:
    def __init__(self, callback):
        self.callback = callback

    def __call__(self, *args, **kwargs):
        def decorator(function):
            self.callback(function, *args, **kwargs)

        return decorator


class script(BaseDecorator):
    def __call__(self,
                 name: str,
                 options: list = None,
                 flags: list = None,
                 pass_args: bool = False,
                 pass_kwargs: bool = False):
        def decorator(function):
            self.callback(function, name, options, flags, pass_args,
                          pass_kwargs)

        return decorator


class no_args(BaseDecorator):
    def __call__(self,
                 options: list = None,
                 flags: list = None,
                 pass_args: bool = False,
                 pass_kwargs: bool = False):
        def decorator(function):
            self.callback(function, options, flags, pass_args)
