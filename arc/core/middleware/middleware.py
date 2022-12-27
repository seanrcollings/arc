import typing as t
import arc.typing as at


class Middleware:
    def __init__(self, app: t.Callable[[at.ExecEnv], t.Any]) -> None:
        self.app = app

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.app!r})"

    def __call__(self, env: at.ExecEnv) -> t.Any:
        return self.app(env)
