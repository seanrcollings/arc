from typing import Any, TypeVar
from getpass import getpass

import arc
from arc.color import fg, effects
from .helpers import write, PREVIOUS_LINE, clear_line
from .questions import Question, QuestionError, ConfirmQuestion, InputQuestion


V = TypeVar("V")


class Prompt:
    """Core class to the `prompt` package.

    Usage:

    ```py
    prompt = Prompt()
    question = MultipleChoiceQuestion(
        "What's you favorite ice cream flavor?",
        ["Chocolate", "Vanilla", "Strawberry"]
    )
    prompt.ask(question)
    ```
    Would result in a prompt like:
    ```
    What's you favorite ice cream flavor?
    [0] Chocolate
    [1] Vanilla
    [2] Strawberry

    >
    ```
    """

    def __init__(
        self, prompt: str = "> ", show_emojis: bool = True, color_output: bool = True
    ):
        """
        Args:
            prompt (str, optional): What to display before the cursor when
                asking a question. Defaults to `'> '`
            show_emojis (bool, optional): Whether or not to display the
                icons / emojis when arc.printing messages with the display
                methods below. Defaults to True.
            color_output (bool, optional): [description]. Whether or not
                do color the output of each of the display methods below.
                Defaults to True.
        """
        self.prompt = prompt
        self.show_emojis = show_emojis
        self.color_output = color_output
        self._previous_answers: list[Any] = []

    @property
    def previous_answers(self):
        """All questions asked by this Prompt
        have their answers stored in here"""
        return self._previous_answers

    def ask(self, question: Question[V]) -> V:
        """Ask a question

        Args:
            question (Question[V]): Question object to ask. Each question
                object handles it's rendering and answering differently

        Returns:
            V: The type that the particular Question returns
        """

        # TODO: currently, sensitive questions
        # can't display errors
        def get_input(prompt: str):
            if question.sensitive:
                return getpass(prompt)
            return input(prompt)

        if question.multi_line:
            write(question.render() + "\n")

        answer = None
        has_failed = False
        while answer is None:
            user_input = get_input(
                (PREVIOUS_LINE if has_failed else "")
                + clear_line()
                + (question.render() if not question.multi_line else "")
                + self.prompt
            )

            try:
                answer = question.handle_answer(user_input)
            except QuestionError as e:
                write(clear_line())
                self.error(str(e), end="")
                has_failed = True

        write("\n")  # get past the error message
        self._previous_answers.append(answer)
        return answer

    def confirm(self, *args, **kwargs) -> bool:
        """Request a Y/N answer from the user

        Args:
            desc (str): Message to display to the user

        Returns:
            bool: The user's answer to the question
        """
        question = ConfirmQuestion(*args, **kwargs)
        return self.ask(question)

    def input(
        self,
        desc: str,
        empty: bool = True,
        sensitive: bool = False,
        multi_line: bool = False,
    ) -> str:
        """Gather input from stdin

        Is an alias for the `InputQuestion` type

        Args:
            desc (str): Message to display to the user
            empty (bool): Whether an empty imput should be allowed
            sensitive (bool): If The data is sensitive, input won't be echoed to the command line

        Returns:
            str: The user's input
        """
        question = InputQuestion(desc, empty, sensitive, multi_line)
        return self.ask(question)

    def beautify(self, message: str, color: str = "", emoji: str = "", **kwargs):
        arc.print(
            self.colored(color) + self.emoji(emoji) + message + effects.CLEAR, **kwargs
        )

    def error(self, message: str, **kwargs):
        """Display an error message to the user"""
        self.beautify(message, fg.RED, "🚨", **kwargs)

    def ok(self, message: str, **kwargs):
        """Display a successful message to the user"""
        self.beautify(message, fg.GREEN, "✓", **kwargs)

    def no(self, message: str, **kwargs):
        """Display an unsuccessful message to the user"""
        self.beautify(message, fg.RED, "✗", **kwargs)

    def act(self, message: str, **kwargs):
        """Display an action message to the user"""
        self.beautify(message, fg.BRIGHT_BLUE, **kwargs)

    def warn(self, message: str, **kwargs):
        """Display a warning message to the user"""
        self.beautify(message, fg.YELLOW, "🚧", **kwargs)

    def subtle(self, message: str, **kwargs):
        """ "Display a subtle (light grey) message to the user"""
        self.beautify(message, fg.GREY, **kwargs)

    def snake(self, message: str, **kwargs):
        """Display a Pythonic message to the user"""
        self.beautify(message, emoji="🐍", **kwargs)

    def emoji(self, emoji: str):
        if self.show_emojis and len(emoji) > 0:
            return emoji + " "
        return ""

    def colored(self, color: str):
        if self.color_output:
            return color
        return ""
