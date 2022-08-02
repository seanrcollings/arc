from __future__ import annotations
import itertools
from logging import Logger
import typing as t
import contextlib

from arc import errors, utils
from arc import _command
from arc.color import colorize, fg
from arc.config import config
from arc.prompt.prompt import Prompt
from arc.types.state import State
from arc.logging import logger
from arc.present import Joiner
import arc.typing as at

if t.TYPE_CHECKING:
    from arc._command.param.param import ValueOrigin


T = t.TypeVar("T")


class Context:
    _stack: list[Context] = []
    command: _command.Command
    _exit_stack: contextlib.ExitStack
    _stack_count: int
    args: dict[str, t.Any]
    rest: list[str]
    arg_origins: dict[str, ValueOrigin]

    config = config
    logger: Logger = logger
    state: State = State()

    def __init__(
        self,
        command: _command.Command,
        parent: Context | None = None,
    ) -> None:
        self.command = command
        self.parent = parent
        self.rest = []
        self._stack_count = 0
        self._exit_stack = contextlib.ExitStack()
        self.arg_origins = {}

    def __repr__(self) -> str:
        return f"Context({self.command!r})"

    def __enter__(self) -> Context:
        if self._stack_count == 0:
            self.logger.debug(f"Entering Context: {self!r}")
        self._stack_count += 1
        Context.push(self)
        return self

    def __exit__(self, exc_type, exc_value, trace) -> None:
        self._stack_count -= 1
        Context.pop()
        if self._stack_count == 0:
            self.logger.debug(f"Closing Context: {self!r}")
            self.close()

    @classmethod
    def __depends__(self, ctx: Context) -> Context:
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
            raise errors.ArcError("No contexts exist")

        return cls._stack[-1]

    @property
    def root(self) -> Context:
        """Retrieves the root context object"""
        curr = self
        while curr.parent:
            curr = curr.parent

        return curr

    @property
    def prompt(self) -> Prompt:
        return self.config.prompt

    def close(self) -> None:
        self._exit_stack.close()

    def run(self, args: list[str]) -> t.Any:
        parsed = self.parse_args(args)
        processed, missing = self.command.process_parsed_result(parsed, self)

        if missing:
            params = ", ".join(colorize(param.cli_name, fg.YELLOW) for param in missing)
            raise errors.MissingArgError(
                f"The following arguments are required: {params}", self
            )

        self.command.inject_dependancies(processed, self)
        self.args = processed
        decostack = self.command.decorators()
        decostack.start(self)

        try:
            res = self.execute(self.command.callback, **processed)
        except Exception as e:
            res = None
            decostack.throw(e)
        else:
            decostack.close()

        return res

    def execute(
        self, callback: t.Union[_command.Command, t.Callable], **kwargs
    ) -> t.Any:
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

    def parse_args(self, args: list[str]) -> at.ParseResult:
        if args:
            parsed, rest = self.command.parse_args(args, self)

            if rest and not self.config.allow_unrecognized_args:
                message = f"Unrecognized arguments: {Joiner.with_space(rest, style=fg.YELLOW)}"

                message += self.__get_suggestions(rest)
                list(
                    itertools.chain(
                        *[param.get_param_names() for param in self.command.key_params]
                    )
                )
                raise errors.UnrecognizedArgError(message, self)
            else:
                self.rest = rest
        else:
            parsed = {}

        return parsed

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

    def __get_suggestions(self, rest: list[str]) -> str:
        message = ""

        if self.config.suggestions["suggest_commands"]:

            message += self.__fmt_suggestions(
                rest[0:1],
                list(
                    itertools.chain(
                        *[com.all_names for com in self.command.subcommands.values()]
                    )
                ),
                "subcommand",
            )

        if self.config.suggestions["suggest_params"]:
            message += self.__fmt_suggestions(
                rest,
                list(
                    itertools.chain(
                        *[param.get_param_names() for param in self.command.key_params]
                    )
                ),
                "argument",
            )

        return message

    def __fmt_suggestions(self, rest: list[str], possibilities: list[str], kind: str):
        message = ""

        suggestions = utils.string_suggestions(
            rest, possibilities, self.config.suggestions["distance"]
        )

        for param_name, param_sug in suggestions.items():
            if param_sug:
                message += (
                    f"\nUnrecognized {kind} {colorize(param_name, fg.YELLOW)}, "
                    f"did you mean: {Joiner.with_or(param_sug, style=fg.YELLOW)}"
                )

        return message
