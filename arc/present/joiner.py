import typing as t

from arc import color


class Join:
    @staticmethod
    def together(
        values: t.Iterable[t.Any],
        string: str = "",
        remove_falsey: bool = False,
        style: str = None,
    ) -> str:
        if remove_falsey:
            values = [v for v in values if v]

        if style:
            return string.join(color.colorize(v, style) for v in values)

        return string.join(str(v) for v in values)

    @staticmethod
    def with_space(values: t.Iterable[t.Any], *args: t.Any, **kwargs: t.Any) -> str:
        return Join.together(values, " ", *args, **kwargs)

    @staticmethod
    def with_comma(values: t.Iterable[t.Any], *args: t.Any, **kwargs: t.Any) -> str:
        return Join.together(values, ", ", *args, **kwargs)

    @staticmethod
    def with_newline(values: t.Iterable[t.Any], *args: t.Any, **kwargs: t.Any) -> str:
        return Join.together(values, "\n", *args, **kwargs)

    @staticmethod
    def in_groups(
        first: t.Iterable[t.Any],
        second: t.Iterable[t.Any],
        string: str,
        between: str,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> str:
        """Joins two groups objects with `string`, then joins the two groups together with `between`"""
        return Join.together(
            (
                Join.together(first, string, *args, **kwargs),
                Join.together(second, string, *args, **kwargs),
            ),
            between,
        )

    @staticmethod
    def with_last(
        values: t.Sequence[t.Any],
        string: str,
        last_string: str,
        *args: t.Any,
        **kwargs: t.Any,
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

        if len(values) == 1:
            return Join.together(values, "", *args, **kwargs)

        return Join.in_groups(
            values[:-1], [values[-1]], string, last_string, *args, **kwargs
        )

    @staticmethod
    def with_and(values: t.Sequence[t.Any]) -> str:
        """Joins a Sequence of items with commas
        and an "and" at the end

        Args:
            values (Sequence): Values to join

        Returns:
            string: joined values
        """
        return Join.with_last(values, ", ", " and ")

    @staticmethod
    def with_or(values: t.Sequence[t.Any], *args: t.Any, **kwargs: t.Any) -> str:
        """Joins a Sequence of items with commas
        and an "or" at the end

        [1, 2, 3, 4] -> "1, 2, 3 or 4"

        Args:
            values (Sequence): Values to join

        Returns:
            string: joined values
        """

        return Join.with_last(values, ", ", " or ", *args, **kwargs)
