from __future__ import annotations

import argparse
import enum
import typing as t
from gettext import gettext as _

import arc
import arc.typing as at
from arc import errors
from arc._command.param import Action, Param
from arc.autocompletions import completions
from arc.color import fg
from arc.config import config
from arc.context import Context
from arc.present.helpers import Joiner
from arc.utils import safe_issubclass

if t.TYPE_CHECKING:
    from arc._command.command import Command


class Parser(argparse.ArgumentParser):
    def parse_intermixed_args(  # type: ignore
        self, args: t.Sequence[str] | None = None, namespace=None
    ) -> at.ParseResult:
        res = super().parse_intermixed_args(args, namespace)
        return dict(res._get_kwargs())

    def parse_known_intermixed_args(  # type: ignore
        self, args: t.Sequence[str] | None = None, namespace=None
    ) -> tuple[at.ParseResult, list[str]]:
        parsed, rest = super().parse_known_intermixed_args(args, namespace)
        return (dict(parsed._get_kwargs()), rest)

    def add_param(self, param: Param, command: Command):
        kwargs: dict[str, t.Any] = {}

        kwargs["action"] = (
            param.action.value if isinstance(param.action, Action) else param.action
        )

        if (default := param.parser_default) is not None:
            kwargs["default"] = default

        if safe_issubclass(param.action, CustomAction):
            kwargs["command"] = command

        if param.action is Action.STORE:
            kwargs["nargs"] = param.nargs

        if not param.is_argument:
            kwargs["dest"] = param.argument_name

        self.add_argument(*param.get_param_names(), **kwargs)

    # NOTE: This method is almost entirely lifted from
    # the actual argparse implementation, because
    # argparse's error handling cusomization is doodoo
    # All modificatiosn to this method will be marked
    def _parse_known_args(self, arg_strings, namespace):
        # replace arg strings that are file references
        if self.fromfile_prefix_chars is not None:
            arg_strings = self._read_args_from_files(arg_strings)

        # map all mutually exclusive arguments to the other arguments
        # they can't occur with
        action_conflicts = {}
        for mutex_group in self._mutually_exclusive_groups:
            group_actions = mutex_group._group_actions
            for i, mutex_action in enumerate(mutex_group._group_actions):
                conflicts = action_conflicts.setdefault(mutex_action, [])
                conflicts.extend(group_actions[:i])
                conflicts.extend(group_actions[i + 1 :])

        # find all option indices, and determine the arg_string_pattern
        # which has an 'O' if there is an option at an index,
        # an 'A' if there is an argument, or a '-' if there is a '--'
        option_string_indices = {}
        arg_string_pattern_parts = []
        arg_strings_iter = iter(arg_strings)
        for i, arg_string in enumerate(arg_strings_iter):

            # all args after -- are non-options
            if arg_string == "--":
                arg_string_pattern_parts.append("-")
                for arg_string in arg_strings_iter:
                    arg_string_pattern_parts.append("A")

            # otherwise, add the arg to the arg strings
            # and note the index if it was an option
            else:
                option_tuple = self._parse_optional(arg_string)
                if option_tuple is None:
                    pattern = "A"
                else:
                    option_string_indices[i] = option_tuple
                    pattern = "O"
                arg_string_pattern_parts.append(pattern)

        # join the pieces together to form the pattern
        arg_strings_pattern = "".join(arg_string_pattern_parts)

        # converts arg strings to the appropriate and then takes the action
        seen_actions = set()
        seen_non_default_actions = set()

        def take_action(action, argument_strings, option_string=None):
            seen_actions.add(action)
            argument_values = self._get_values(action, argument_strings)

            # error if this argument is not allowed with other previously
            # seen arguments, assuming that actions that use the default
            # value don't really count as "present"
            if argument_values is not action.default:
                seen_non_default_actions.add(action)
                for conflict_action in action_conflicts.get(action, []):
                    if conflict_action in seen_non_default_actions:
                        msg = _("not allowed with argument %s")
                        action_name = argparse._get_action_name(conflict_action)
                        raise argparse.ArgumentError(action, msg % action_name)

            # take the action if we didn't receive a SUPPRESS value
            # (e.g. from a default)
            if argument_values is not argparse.SUPPRESS:
                action(self, namespace, argument_values, option_string)

        # function to convert arg_strings into an optional action
        def consume_optional(start_index):

            # get the optional identified at this index
            option_tuple = option_string_indices[start_index]
            action, option_string, explicit_arg = option_tuple

            # identify additional optionals in the same arg string
            # (e.g. -xyz is the same as -x -y -z if no args are required)

            # MODIFIED ------------------------------------------
            def _wrapped_match_argument(action, args_str_pattern):
                try:
                    return self._match_argument(action, args_str_pattern)
                except argparse.ArgumentError as e:
                    raise errors.ParserError(str(e)) from e

            match_argument = _wrapped_match_argument
            # ORIGINAL ------------------------------------------
            # match_argument = self._match_argument
            # ---------------------------------------------------
            action_tuples = []
            while True:

                # if we found no optional action, skip it
                if action is None:
                    extras.append(arg_strings[start_index])
                    return start_index + 1

                # if there is an explicit argument, try to match the
                # optional's string arguments to only this
                if explicit_arg is not None:
                    arg_count = match_argument(action, "A")

                    # if the action is a single-dash option and takes no
                    # arguments, try to parse more single-dash options out
                    # of the tail of the option string
                    chars = self.prefix_chars
                    if arg_count == 0 and option_string[1] not in chars:
                        action_tuples.append((action, [], option_string))
                        char = option_string[0]
                        option_string = char + explicit_arg[0]
                        new_explicit_arg = explicit_arg[1:] or None
                        optionals_map = self._option_string_actions
                        if option_string in optionals_map:
                            action = optionals_map[option_string]
                            explicit_arg = new_explicit_arg
                        else:
                            msg = _("ignored explicit argument %r")
                            raise argparse.ArgumentError(action, msg % explicit_arg)

                    # if the action expect exactly one argument, we've
                    # successfully matched the option; exit the loop
                    elif arg_count == 1:
                        stop = start_index + 1
                        args = [explicit_arg]
                        action_tuples.append((action, args, option_string))
                        break

                    # error if a double-dash option did not use the
                    # explicit argument
                    else:
                        msg = _("ignored explicit argument %r")
                        raise argparse.ArgumentError(action, msg % explicit_arg)

                # if there is no explicit argument, try to match the
                # optional's string arguments with the following strings
                # if successful, exit the loop
                else:
                    start = start_index + 1
                    selected_patterns = arg_strings_pattern[start:]
                    arg_count = match_argument(action, selected_patterns)
                    stop = start + arg_count
                    args = arg_strings[start:stop]
                    action_tuples.append((action, args, option_string))
                    break

            # add the Optional to the list and return the index at which
            # the Optional's string args stopped
            assert action_tuples
            for action, args, option_string in action_tuples:
                take_action(action, args, option_string)
            return stop

        # the list of Positionals left to be parsed; this is modified
        # by consume_positionals()
        positionals = self._get_positional_actions()

        # function to convert arg_strings into positional actions
        def consume_positionals(start_index):
            # match as many Positionals as possible
            match_partial = self._match_arguments_partial
            selected_pattern = arg_strings_pattern[start_index:]
            arg_counts = match_partial(positionals, selected_pattern)

            # slice off the appropriate arg strings for each Positional
            # and add the Positional and its args to the list
            for action, arg_count in zip(positionals, arg_counts):
                args = arg_strings[start_index : start_index + arg_count]
                start_index += arg_count
                take_action(action, args)

            # slice off the Positionals that we just parsed and return the
            # index at which the Positionals' string args stopped
            positionals[:] = positionals[len(arg_counts) :]
            return start_index

        # consume Positionals and Optionals alternately, until we have
        # passed the last option string
        extras = []
        start_index = 0
        if option_string_indices:
            max_option_string_index = max(option_string_indices)
        else:
            max_option_string_index = -1
        while start_index <= max_option_string_index:

            # consume any Positionals preceding the next option
            next_option_string_index = min(
                [index for index in option_string_indices if index >= start_index]
            )
            if start_index != next_option_string_index:
                positionals_end_index = consume_positionals(start_index)

                # only try to parse the next optional if we didn't consume
                # the option string during the positionals parsing
                if positionals_end_index > start_index:
                    start_index = positionals_end_index
                    continue
                else:
                    start_index = positionals_end_index

            # if we consumed all the positionals we could and we're not
            # at the index of an option string, there were extra arguments
            if start_index not in option_string_indices:
                strings = arg_strings[start_index:next_option_string_index]
                extras.extend(strings)
                start_index = next_option_string_index

            # consume the next optional and any arguments for it
            start_index = consume_optional(start_index)

        # consume any positionals following the last Optional
        stop_index = consume_positionals(start_index)

        # if we didn't consume all the argument strings, there were extras
        extras.extend(arg_strings[stop_index:])

        # make sure all required actions were present and also convert
        # action defaults which were not given as arguments
        required_actions = []
        for action in self._actions:
            if action not in seen_actions:
                if action.required:
                    required_actions.append(argparse._get_action_name(action))
                else:
                    # Convert action default now instead of doing it before
                    # parsing arguments to avoid calling convert functions
                    # twice (which may fail) if the argument was given, but
                    # only if it was defined already in the namespace
                    if (
                        action.default is not None
                        and isinstance(action.default, str)
                        and hasattr(namespace, action.dest)
                        and action.default is getattr(namespace, action.dest)
                    ):
                        setattr(
                            namespace,
                            action.dest,
                            self._get_value(action, action.default),
                        )

        if required_actions:
            # MODIFIED -----------------------------------------------------------
            self.error(
                _("the following arguments are required: %s")
                % Joiner.with_comma(required_actions, style=(fg.YELLOW))
            )
            # ORIGINAL -----------------------------------------------------------
            # self.error(
            #     _("the following arguments are required: %s")
            #     % ", ".join(required_actions)
            # )
            # --------------------------------------------------------------------

        # make sure all required groups had one option present
        for group in self._mutually_exclusive_groups:
            if group.required:
                for action in group._group_actions:
                    if action in seen_non_default_actions:
                        break

                # if no actions were used, report the error
                else:
                    names = [
                        argparse._get_action_name(action)
                        for action in group._group_actions
                        if action.help is not argparse.SUPPRESS
                    ]
                    msg = _("one of the arguments %s is required")
                    self.error(msg % " ".join(names))

        # return the updated namespace and the extra arguments
        return namespace, extras

    def error(self, message: str) -> t.NoReturn:
        raise errors.ParserError(message)

    def exit(self, status: int = 0, message: str | None = None) -> t.NoReturn:
        raise errors.Exit(status, message)


class CustomAction(argparse.Action):
    def __init__(self, *args, command: Command, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.command = command


class CustomHelpAction(CustomAction, argparse._HelpAction):
    def __call__(self, *args, **kwargs):
        arc.print(self.command.doc.help())
        raise errors.Exit()


class CustomVersionAction(CustomAction, argparse._VersionAction):
    def __call__(self, *args, **kwargs):
        arc.print(config.version)
        raise errors.Exit()


class CustomAutocompleteAction(CustomAction, argparse._StoreAction):
    def __call__(self, _parser, _ns, value, *args, **kwargs):
        arc.print(completions(value, Context.current()), end="")
        raise errors.Exit()
