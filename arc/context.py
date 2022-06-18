from __future__ import annotations
import typing as t
import contextlib

from arc import errors
from arc import _command
from arc._command.decorators import DecoratorStack
from arc.color import colorize, fg
from arc.config import config
from arc.types.state import State

T = t.TypeVar("T")


class Context:
    _stack: list[Context] = []
    command: _command.Command
    _exit_stack: contextlib.ExitStack
    _stack_count: int
    rest: list[str]

    config = config
    _state: dict[str, t.Any] = {}
    state: State = State(_state)

    def __init__(
        self,
        command: _command.Command,
        parent: Context | None = None,
        state: dict | None = None,
    ) -> None:
        self.command = command
        self.parent = parent
        self.rest = []
        self._stack_count = 0
        self._exit_stack = contextlib.ExitStack()

    def __repr__(self):
        return f"Context({self.command!r})"

    def __enter__(self):
        self._stack_count += 1
        Context.push(self)
        return self

    def __exit__(self, exc_type, exc_value, trace):
        self._stack_count -= 1
        Context.pop()
        if self._stack_count == 0:
            self.close()

    @classmethod
    def __depends__(self, ctx: Context):
        return ctx

    @classmethod
    def push(cls, ctx: Context) -> None:
        """Pushes a context onto the internal stack"""
        cls._stack.append(ctx)

    @classmethod
    def pop(cls) -> Context:
        """Pops a context off the internal stack"""
        return cls._stack.pop()

    @classmethod
    def current(cls) -> Context:
        """Returns the current context"""
        if not cls._stack:
            raise RuntimeError("No contexts exist")

        return cls._stack[-1]

    @property
    def root(self):
        """Retrieves the root context object"""
        curr = self
        while curr.parent:
            curr = curr.parent

        return curr

    @property
    def prompt(self):
        return self.config.prompt

    def close(self):
        self._exit_stack.close()

    def run(self, args: list[str]):
        if args:
            parser = self.command.create_parser()
            parsed, rest = parser.parse_known_intermixed_args(args)
            if rest and not self.config.allow_unrecognized_args:
                raise errors.UnrecognizedArgError(
                    f"Unrecognized arguments: {' '.join(rest)}", self
                )
            else:
                self.rest = rest
        else:
            parsed = {}

        processed, missing = self.command.process_parsed_result(parsed, self)

        if missing:
            params = ", ".join(colorize(param.cli_name, fg.YELLOW) for param in missing)
            raise errors.MissingArgError(
                f"The following arguments are required: {params}", self
            )

        self.command.inject_dependancies(processed, self)
        deco_stack = DecoratorStack()
        for deco in reversed(self.command.decorators):
            deco_stack.add(deco.func(processed, self))

        try:
            res = self.execute(self.command.callback, **processed)
        except Exception as e:
            res = None
            deco_stack.throw(e)
        else:
            deco_stack.close()

        return res

    def execute(self, callback: t.Union[_command.Command, t.Callable], **kwargs):
        """Can be called in two ways

        1. if `callback` is a function / callable, all other kwargs
        will simply be forwarded to the function.
        2. if `callback` is a command, kwargs will still be forwarded,
        arc will fill in defaults, and the current execution's state
        will be used initially
        """

        if isinstance(callback, _command.Command):
            ctx = self.create_child(callback)
            cmd = callback
            callback = cmd.callback
            cmd.inject_dependancies(kwargs, ctx)

        else:
            ctx = self

        with ctx:
            return callback(**kwargs)

    def create_child(self, command: _command.Command) -> Context:
        """Creates a new context that is the child of the current context"""
        return type(self)(command, parent=self)

    def resource(self, resource: t.ContextManager[T]) -> T:
        """Opens a resource like you would with the `with` statement.
        When this context is closed, all open resources will be closed
        along with it
        """
        return self._exit_stack.enter_context(resource)

    def close_callback(
        self, callback: t.Callable[..., t.Any]
    ) -> t.Callable[..., t.Any]:
        """Adds a callback that will be executed when this context is closed"""
        return self._exit_stack.callback(callback)

    def exit(self, code: int = 0) -> t.NoReturn:
        """Exits the app with code `code`"""
        raise errors.Exit(code)
