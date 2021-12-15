from __future__ import annotations
import contextlib
import typing as t

if t.TYPE_CHECKING:
    from arc.command import Command


# Context Goals:
# - Handles all state surrounding command execution
# - Makes execution of additional commands durning the execution of a specific command simple
# - Central container for context managers
# - Simplifies various implementation details because they will not be centeralized, rather than dispersed
# - Will handle the actual execution of a command with a .run() or .execute() or something


class AppContext:
    """AppContext holds all state relevant to command execution

    Attributes:
        command (Command): The command for this context
        parent (AppContext, optional): The parent Context. Defaults to None.
        fullname (str, optional): The most descriptive name for this invocatio. Defaults to None.
        args (dict[str, typing.Any]): mapping of argument names to parsed values
        extra (list[str]): extra input that may not have been parsed
    """

    # Each time a command is invoked,
    # an instance of AppContext is pushed onto
    # this stack. When execution completes, the
    # context will be popped off the stack
    __stack: list[AppContext] = []

    def __init__(self, command: Command, fullname: str, parent: AppContext = None):
        self.command = command
        self.parent = parent
        self.fullname = fullname

        self.args: dict[str, t.Any] = {}
        self.extra: list[str] = []

        # Keeps track of how many times this context has been pusehd onto the context
        # stack. When it reaches zero, ctx.close() will be called
        self._stack_count = 0

    def __repr__(self):
        return f"AppContext({self.command!r})"

    def __enter__(self):
        self._stack_count += 1
        AppContext.push(self)
        return self

    def __exit__(self, exc_type, exc_value, trace):
        self._stack_count -= 1
        AppContext.pop()
        if self._stack_count == 0:
            self.close()

    @property
    def root(self):
        """Retrieves the root context object"""
        curr = self
        while curr.parent:
            curr = curr.parent

        return curr

    def child_context(self, command: Command) -> AppContext:
        """Creates a new context that is the child of the current context"""
        return type(self)(command, parent=self, fullname=command.name)

    def execute(self, callback: t.Union[Command, t.Callable], *args, **kwargs):
        return callback(*args, **kwargs)

    def close(self):
        ...

    @classmethod
    def push(cls, ctx: AppContext) -> None:
        """Pushes a context onto the internal stack"""
        cls.__stack.append(ctx)

    @classmethod
    def pop(cls) -> AppContext:
        """Pops a context off the internal stack"""
        return cls.__stack.pop()

    @classmethod
    def current(cls) -> AppContext:
        """Returns the current context"""
        if not cls.__stack:
            raise RuntimeError("No contexts exist")

        return cls.__stack[-1]
