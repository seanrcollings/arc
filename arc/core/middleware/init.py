from __future__ import annotations
import typing as t
import shlex
import sys

import arc
from arc import errors
from arc import typing as at
from arc.parser import Parser
from arc.core.middleware.middleware import Middleware

if t.TYPE_CHECKING:
    from arc.core import Command


class InitChecksMiddleware(Middleware):
    def __call__(self, env: at.ExecEnv):
        root: Command = env["arc.root"]

        if root.subcommands and len(list(root.argument_params)) != 0:
            raise errors.CommandError(
                "Top-level command with subcommands cannot "
                "have argument / positional parameters"
            )

        return self.app(env)


class AddUsageErrorInfoMiddleware(Middleware):
    """A utility middleware that catches `UsageError`s and adds information so they can generate a usage error

    # Env Dependancies
    - `arc.command` (optional): Usage information comes from the current executing [`Command`][arc.core.command.Command] object
    # Env Additions
    None
    """

    def __call__(self, env: at.ExecEnv) -> t.Any:
        try:
            return self.app(env)
        except errors.UsageError as e:
            e.command = env.get("arc.command")
            raise


class InputMiddleware(Middleware):
    """Middleware that normalizes different input sources. If input is provided when
    command is called, it will be normalized to an list. If input is not provided,
    `sys.argv` is used.

    # Env Dependancies
    - `arc.input` (optional): Only exists if input was provided in the call to the command

    # Env Additions
    - `arc.input`: Adds it if it's not already there, normalizes it if it is there
    """

    def __call__(self, env) -> t.Any:
        args: at.InputArgs = env.get("arc.input")
        if args is None:
            args = sys.argv[1:]

        if isinstance(args, str):
            args = shlex.split(args)

        args = list(args)
        env["arc.input"] = args

        return self.app(env)


class CommandFinderMiddleware(Middleware):
    def __call__(self, env: at.ExecEnv):
        args: list[str] = env["arc.input"]
        root: Command = env["arc.root"]
        global_args, command, command_args = root.split_args(args)
        env["arc.input.global"] = global_args
        env["arc.command"] = command
        env["arc.input"] = command_args
        env["arc.mode"] = self.get_mode(root, command)

        return self.app(env)

    def get_mode(self, root: Command, command: Command) -> at.ExecMode:
        if root is command:
            if root.subcommands:
                return "global"
            else:
                return "single"
        else:
            return "subcommand"


class ArgParseMiddleware(Middleware):
    def __call__(self, env: at.ExecEnv):
        command: Command = env["arc.command"]
        args: list[str] = env["arc.input"]
        global_args: list[str] = env["arc.input.global"]
        root: Command = env["arc.root"]
        mode: at.ExecMode = env["arc.mode"]

        if mode == "single":
            return self.run_command(command, global_args, env)
        elif mode == "global":
            self.parse_args(command, global_args)
            arc.usage(command)
            arc.exit(1)
        elif mode == "subcommand":
            if not root.is_namespace:
                env["arc.command"] = root
                self.run_command(root, global_args, env)
                env["arc.command"] = command
                del env["arc.args"]
            return self.run_command(command, args, env)

    def run_command(self, command: Command, args: list[str], env: at.ExecEnv):
        result, extra = self.parse_args(command, args)

        env["arc.parse.result"] = result
        env["arc.parse.extra"] = extra

        return self.app(env)

    def parse_args(self, command: Command, args: list[str]) -> tuple[dict, list[str]]:
        parser = self.create_parser(command)

        return parser.parse_known_intermixed_args(args)

    def create_parser(self, command: Command) -> Parser:
        parser = Parser(add_help=False)
        for param in command.cli_params:
            parser.add_param(param, command)

        return parser
