from __future__ import annotations
import contextlib
import sys
import typing as t

from arc import errors, logging, typing as at
from arc.config import config
from arc.types.params import special
from arc import _command as command
from arc.types.state import State
from arc.typing import Suggestions
from arc.utils import IoWrapper

if t.TYPE_CHECKING:
    from arc._command import Command

logger = logging.getArcLogger("ctx")


T = t.TypeVar("T")

default_sug: Suggestions = {
    "levenshtein_distance": 2,
    "suggest_arguments": True,
    "suggest_commands": True,
}


@special(default=object())
class Context:
    """Context holds all state relevant to a command execution

    The current context can be accessed with `Context.current()`. If
    you want acces to it inside of a command, you can do so easily
    by simply annotating an argument with this type.

    Attributes:
        command (Command): The command for this context
        parent (Context, optional): The parent Context. Defaults to None.
        fullname (str, optional): The most descriptive name for this invocatio. Defaults to None.
        args (dict[str, typing.Any]): mapping of argument names to parsed values
        extra (list[str]): extra input that may not have been parsed
        command_chain (list[str]): The chain of commands between the executing command and the
        `CLI` root. If a command is executing standalone, this will always be empty
    """

    # Each time a command is invoked,
    # an instance of Context is pushed onto
    # this stack. When execution completes, the
    # context will be popped off the stack
    __stack: list[Context] = []
    config = config

    def __init__(
        self,
        command: Command,
        fullname: str,
        command_chain: list[Command] = None,
        parent: Context = None,
        suggestions: Suggestions = None,
    ):
        self.command = command
        self.fullname = fullname
        self.command_chain = command_chain or []
        self.parent = parent

        if suggestions is not None:
            self.suggestions = default_sug | suggestions
        else:
            self.suggestions = default_sug

        self.args: dict[str, t.Any] = {}
        self.extra: list[str] = []
        self._state: t.Optional[State] = None

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

    @property
    def state(self):
        if self._state is None:
            state: dict = {}
            if self.command_chain:
                for cmd in self.command_chain:
                    state |= cmd.state

                self._state = State(state)
            else:
                self._state = State(self.command.state)

        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def child_context(self, command: Command) -> Context:
        """Creates a new context that is the child of the current context"""
        return type(self)(command, parent=self, fullname=command.name)

    def execute(self, callback: t.Union[Command, t.Callable], **kwargs):
        """Can be called in two ways

        1. if `callback` is a function / callable, all other kwargs
        will simply be forwarded to the function.
        2. if `callback` is a command, kwargs will still be forwarded,
        arc will fill in defaults, and the current execution's state
        will be used initially
        """

        if isinstance(callback, command.Command):
            ctx = self.child_context(callback)
            ctx.state = self.state | ctx.state
            cmd = callback
            callback = cmd.callback

            for param in cmd.params:
                if param.arg_name not in kwargs and param.expose:
                    kwargs[param.arg_name] = param.convert(param.default, ctx)

        else:
            ctx = self

        with ctx:
            return callback(**kwargs)

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
        """Recieve access to the current ctx in commands"""
        return ctx
