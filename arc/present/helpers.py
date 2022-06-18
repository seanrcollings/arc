import typing as t


class Joiner:
    @staticmethod
    def join(values: t.Iterable, string: str, remove_falsey: bool = False):
        if remove_falsey:
            values = [v for v in values if v]

        return string.join(str(v) for v in values)

    @staticmethod
    def with_space(values: t.Sequence, remove_falsey: bool = False):

        return Joiner.join(values, " ", remove_falsey)

    @staticmethod
    def with_last(values: t.Sequence, string: str, last_string: str):
        """Joins values together with an additional `last_string` to format how
        the final value is joined to the rest of the list

        Args:
            values (Sequence): Values to join
            string (str): What to join values 0 - penultimate value with.
            last_string (str): What to use to join the last value to the rest.
        """
        if len(values) == 1:
            return values[0]

        return Joiner.join(values[:-1], string) + last_string + str(values[-1])

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
    def with_or(values: t.Sequence):
        """Joins a Sequence of items with commas
        and an or at the end

        [1, 2, 3, 4] -> "1, 2, 3 or 4"

        Args:
            values (Sequence): Values to join

        Returns:
            str: joined values
        """

        return Joiner.with_last(values, ", ", " or ")