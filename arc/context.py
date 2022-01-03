from __future__ import annotations
import contextlib
import os
import typing as t

from arc import errors, logging, typing as at
from arc.callback import CallbackStack
from arc.color import colorize, fg
from arc.config import config
from arc import _command
from arc.params import special
from arc.types.state import State
from arc.prompt import Prompt


if t.TYPE_CHECKING:
    from arc._command import Command

logger = logging.getArcLogger("ctx")


T = t.TypeVar("T")

default_sug: at.Suggestions = {
    "levenshtein_distance": 2,
    "suggest_arguments": True,
    "suggest_commands": True,
}

default_prompt = Prompt("> ")


@special(default=object())
class Context:
    """Context holds all state relevant to a command execution

    The current context can be accessed with `Context.current()`. If
    you want acces to it inside of a command, you can do so easily
    by simply annotating an argument with this type.

    Attributes:
        command (Command): The command for this context
        parent (Context, optional): The parent Context.
        fullname (str, optional): The most descriptive name for this invocation.
        args (dict[str, typing.Any]): mapping of argument names to parsed values
        extra (list[str]): extra input that may not have been parsed
        command_chain (list[str]): The chain of commands between the executing command and the
            `CLI` root. If a command is executing standalone, this will always be empty
        execute_callbacks (bool): whether or not to execute command callbacks
            when executing the command
        env_prefix: (str, optional): A prefix to use when selecting values from environmental
            variables. Will be combined with the name specified for a parameter.
        prompt: (arc.prompt.Prompt, optional): A prompt object will be used when prompting
            for parameter values.
    """

    # Each time a command is invoked,
    # an instance of Context is pushed onto
    # this stack. When execution completes, the
    # context will be popped off the stack
    __stack: list[Context] = []
    config = config
    _meta: dict[str, t.Any] = {}

    def __init__(
        self,
        command: Command,
        fullname: str,
        command_chain: list[Command] = None,
        parent: Context = None,
        suggestions: at.Suggestions = None,
        execute_callbacks: bool = True,
        env_prefix: str = "",
        prompt: Prompt = None,
    ):
        self.command = command
        self.fullname = fullname
        self.command_chain = command_chain or []
        self.parent = parent
        self.execute_callbacks = execute_callbacks
        if "prompt" not in self.meta:
            self.meta["prompt"] = prompt or default_prompt
        if "env_prefix" not in self.meta:
            self.meta["env_prefix"] = env_prefix

        if suggestions is not None:
            self.suggestions = default_sug | suggestions
        else:
            self.suggestions = default_sug

        self.args: dict[str, t.Any] = {}
        self.extra: list[str] = []
        self.callback_stack = CallbackStack()
        self.state: State = self.create_state()

        # The result of the most recent execution
        self.result: t.Any = None

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
    def meta(self):
        """Meta is an object that is
        shared globally by all `Context` instances
        """
        return self._meta

    @property
    def prompt(self) -> Prompt:
        return self.meta["prompt"]

    @property
    def env_prefix(self) -> str:
        return self.meta["env_prefix"]

    def create_state(self) -> State:
        state: State = State()
        if self.command_chain:
            for cmd in self.command_chain:
                state.update(cmd.state)
        else:
            state = State(self.command.state)

        if self.parent and self.parent.state:
            state = self.parent.state | state

        return state

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

        if isinstance(callback, _command.Command):
            ctx = self.child_context(callback)
            ctx.state = self.state | ctx.state
            cmd = callback
            callback = cmd._callback

            for param in cmd.params:
                if param.arg_name not in kwargs and param.expose:
                    kwargs[param.arg_name] = param.convert(param.default, ctx)

        else:
            ctx = self

        with ctx:
            cb_stack = CallbackStack()
            if self.execute_callbacks:
                for cb in ctx.command.callbacks:
                    try:
                        cb_stack.add(cb.func(kwargs, ctx))  # type: ignore
                    except AttributeError as e:
                        colored = colorize(str(cb.func.__name__), fg.YELLOW)  # type: ignore
                        raise errors.CallbackError(
                            f"{colored} is not a valid callback. "
                            f"Perhaps you missed a {colorize('yield', fg.ARC_BLUE)}?"
                        ) from e

            with cb_stack:
                ctx.result = callback(**kwargs)
                return ctx.result

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

    def getenv(self, name: str, default):
        return os.getenv(self.env_prefix + name, default)

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
