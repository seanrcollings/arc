from __future__ import annotations
import typing as t
import contextlib

from arc import errors
from arc import _command
from arc.config import config

T = t.TypeVar("T")


class Context:
    _stack: list[Context] = []
    command: _command.Command
    _stack_count = 0
    _exit_stack: contextlib.ExitStack

    config = config

    def __init__(
        self, command: _command.Command, parent: Context | None = None
    ) -> None:
        self.command = command
        self.parent = parent
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

    def close(self):
        self._exit_stack.close()

    def run(self, args: list[str]):
        parser = self.command.create_parser()
        parsed = parser.parse_intermixed_args(args)
        processed = self.command.process_parsed_result(parsed, self)
        self.command.inject_dependancies(processed, self)
        return self.execute(self.command.callback, **processed)

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
            # ctx.state = self.state | ctx.state
            cmd = callback
            callback = cmd.callback

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
