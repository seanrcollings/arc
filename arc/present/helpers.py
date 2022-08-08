import typing as t

from arc.color import colorize


class Joiner:
    @staticmethod
    def join(
        values: t.Iterable,
        string: str,
        remove_falsey: bool = False,
        style: str = None,
    ) -> str:
        if remove_falsey:
            values = [v for v in values if v]

        if style:
            return string.join(colorize(v, *style) for v in values)

        return string.join(str(v) for v in values)

    @staticmethod
    def with_space(values: t.Iterable, *args, **kwargs) -> str:
        return Joiner.join(values, " ", *args, **kwargs)

    @staticmethod
    def with_comma(values: t.Iterable, *args, **kwargs) -> str:
        return Joiner.join(values, ", ", *args, **kwargs)

    @staticmethod
    def in_groups(
        first: t.Iterable,
        second: t.Iterable,
        string: str,
        between: str,
        *args,
        **kwargs
    ) -> str:
        """Joins two groups objects with `string`, then joins the two groups together with `between`"""

        return Joiner.join(
            (
                Joiner.join(first, string, *args, **kwargs),
                Joiner.join(second, string, *args, **kwargs),
            ),
            between,
        )

    @staticmethod
    def with_last(
        values: t.Sequence, string: str, last_string: str, *args, **kwargs
    ) -> str:
        """Joins values together with an additional `last_string` to format how
        the final value is joined to the rest of the list

        Args:
            values (Sequence): Values to join
            string (str): What to join values 0 - penultimate value with.
            last_string (str): What to use to join the last value to the rest.
        """
        if len(values) == 0:
            return ""

        return Joiner.in_groups(
            values[:-1], [values[-1]], string, last_string, *args, **kwargs
        )

    @staticmethod
    def with_and(values: t.Sequence) -> str:
        """Joins a Sequence of items with commas
        and an "and" at the end

        Args:
            values (Sequence): Values to join

        Returns:
            string: joined values
        """
        return Joiner.with_last(values, ", ", " and ")

    @staticmethod
    def with_or(values: t.Sequence, *args, **kwargs) -> str:
        """Joins a Sequence of items with commas
        and an "or" at the end

        [1, 2, 3, 4] -> "1, 2, 3 or 4"

        Args:
            values (Sequence): Values to join

        Returns:
            string: joined values
        """

        return Joiner.with_last(values, ", ", " or ", *args, **kwargs)
