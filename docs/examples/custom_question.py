import re
from typing import Iterable
from arc.prompt import Prompt, Question


class RegexQuestion(Question[str]):
    def __init__(self, prompt: str, pattern: re.Pattern):
        super().__init__()
        self.prompt = prompt
        self.pattern = pattern

    def render(self) -> Iterable[str]:
        """Render should return an iterable of strings
        to output before stopping for input"""
        yield self.prompt
        yield f" [Must match: '{self.pattern.pattern}'] "

    def handle_answer(self, value: str) -> str:
        """The handle answer method checks the validity
        of the user input. In addition, it should perform any
        additional parsing / conversion of the value that is required
        and return that.
        """
        if not self.pattern.match(value):
            self.err(f"Must match pattern: '{self.pattern.pattern}'")

        return value


prompt = Prompt()
question = RegexQuestion("Pick a number", re.compile("\d+"))
number = prompt.ask(question)
print(f"You picked: {number}")
