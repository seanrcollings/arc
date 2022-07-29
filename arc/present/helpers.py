import typing as t

from arc.color import colorize


class Joiner:
    @staticmethod
    def join(
        values: t.Iterable,
        string: str,
        remove_falsey: bool = False,
        style: t.Iterable[str] = None,
    ):
        if remove_falsey:
            values = [v for v in values if v]

        style = style or []

        if style:
            return string.join(colorize(v, *style) for v in values)

        return string.join(str(v) for v in values)

    @staticmethod
    def with_space(values: t.Iterable, *args, **kwargs):
        return Joiner.join(values, " ", *args, **kwargs)

    @staticmethod
    def with_comma(values: t.Iterable, *args, **kwargs):
        return Joiner.join(values, ", ", *args, **kwargs)

    @staticmethod
    def with_last(values: t.Sequence, string: str, last_string: str, *args, **kwargs):
        """Joins values together with an additional `last_string` to format how
        the final value is joined to the rest of the list

        Args:
            values (Sequence): Values to join
            string (str): What to join values 0 - penultimate value with.
            last_string (str): What to use to join the last value to the rest.
        """
        if len(values) == 1:
            return Joiner.join(values, "", *args, **kwargs)

        return (
            Joiner.join(values[:-1], string)
            + last_string
            + str(values[-1], *args, **kwargs)
        )

    @staticmethod
    def with_and(values: t.Sequence):
        """Joins a Sequence of items with commas
        and an "and" at the end

        Args:
            values (Sequence): Values to join

        Returns:
            str: joined values
        """
        return Joiner.with_last(values, ", ", " and ")

    @staticmethod
    def with_or(values: t.Sequence, *args, **kwargs):
        """Joins a Sequence of items with commas
        and an or at the end

        [1, 2, 3, 4] -> "1, 2, 3 or 4"

        Args:
            values (Sequence): Values to join

        Returns:
            str: joined values
        """

        return Joiner.with_last(values, ", ", " or ", *args, **kwargs)
