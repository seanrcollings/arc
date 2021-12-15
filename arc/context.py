from __future__ import annotations
import contextlib
import typing as t

from arc import errors, logging
from arc.config import config
from arc.types.params import as_special_param

if t.TYPE_CHECKING:
    from arc._command import Command

logger = logging.getArcLogger("ctx")


T = t.TypeVar("T")


@as_special_param(default=object())
class Context:
    """Context holds all state relevant to command execution

    Attributes:
        command (Command): The command for this context
        parent (Context, optional): The parent Context. Defaults to None.
        fullname (str, optional): The most descriptive name for this invocatio. Defaults to None.
        args (dict[str, typing.Any]): mapping of argument names to parsed values
        extra (list[str]): extra input that may not have been parsed
    """

    # Each time a command is invoked,
    # an instance of Context is pushed onto
    # this stack. When execution completes, the
    # context will be popped off the stack
    __stack: list[Context] = []
    config = config

    def __init__(self, command: Command, fullname: str, parent: Context = None):
        self.command = command
        self.parent = parent
        self.fullname = fullname

        self.args: dict[str, t.Any] = {}
        self.extra: list[str] = []

        # Keeps track of how many times this context has been pusehd onto the context
        # stack. When it reaches zero, ctx.close() will be called
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

    @property
    def root(self):
        """Retrieves the root context object"""
        curr = self
        while curr.parent:
            curr = curr.parent

        return curr

    def child_context(self, command: Command) -> Context:
        """Creates a new context that is the child of the current context"""
        return type(self)(command, parent=self, fullname=command.name)

    def execute(self, callback: t.Union[Command, t.Callable], *args, **kwargs):
        return callback(*args, **kwargs)

    def close(self):
        logger.debug("Closing %s", self)
        self._exit_stack.close()

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

    @classmethod
    def push(cls, ctx: Context) -> None:
        """Pushes a context onto the internal stack"""
        cls.__stack.append(ctx)

    @classmethod
    def pop(cls) -> Context:
        """Pops a context off the internal stack"""
        return cls.__stack.pop()

    @classmethod
    def current(cls) -> Context:
        """Returns the current context"""
        if not cls.__stack:
            raise RuntimeError("No contexts exist")

        return cls.__stack[-1]

    @classmethod
    def __convert__(cls, _value, _info, ctx: Context):
        return ctx
