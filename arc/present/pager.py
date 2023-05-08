import os
import subprocess

from arc import errors

_reasonable_pagers = [
    "/usr/bin/less",
    "/usr/bin/more",
    "/usr/bin/most",
]


def _get_pager_command() -> str:
    if pager := os.getenv("PAGER", None):
        return pager

    for path in _reasonable_pagers:
        if os.path.exists(path):
            return path

    raise errors.ArcError("No pager found")


def pager(contents: object, command: list[str] | None = None) -> None:
    """Display `contents` in the user's preferred pager.
    Essentially equivalent to
    ```bash
    $ cli-app | less
    ```

    Args:
        contents (str): String contents to display in their page
        command (list[str] | None, optional): Override the default
            pager discovery with a given command to run. Defaults to None.

    Raises:
        ArcError: if no pager can be found for the user
    """
    command = command or [_get_pager_command()]
    subprocess.run(command, input=str(contents).encode("utf-8"))
