#!/usr/bin/env python
import logging
import typing as t
import sys
from pathlib import Path
import shlex
import shutil
import contextlib
from dataclasses import dataclass

import yaml
from arc.config import config as ac

PARENT = Path(__file__).parent
EXAMPLE_DIR = PARENT.parent / "examples"
OUTPUT_DIR = EXAMPLE_DIR / "outputs"


@dataclass
class ExecConfig:
    file: str
    """The file to attempt to load"""
    out: Path
    """The name of the output file"""
    name: str
    """The name of the executable"""
    exit_code: int = 0
    """The expected exit code (if SystemExit is raised)"""
    error_allowed: bool = False
    """Stops errors from termintation execution"""
    exec: t.Union[list[str], str] = ""
    """String to execute the file with. Placed into `argv`"""


def init():
    if OUTPUT_DIR.is_dir():
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir()


def exec_examples(config: list[ExecConfig]):
    for entry in config:
        ac.version = None
        execs = entry.exec
        if isinstance(execs, str):
            execs = [execs]

        with open(EXAMPLE_DIR / entry.file) as f:
            contents = f.read()

        entry.out.parent.mkdir(parents=True, exist_ok=True)

        with entry.out.open("w+") as f:
            print(entry.file, "->", entry.out)
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                for arg in execs:
                    logging.root.handlers.clear()
                    f.write(f"$ python {entry.file} {arg}\n")
                    sys.argv = [entry.file, *shlex.split(arg)]

                    try:
                        exec(contents, {})
                    except SystemExit as e:
                        if e.code != entry.exit_code:
                            raise
                    except Exception:
                        if not entry.error_allowed:
                            raise


def main():
    init()

    with open(PARENT / "exec.yaml", "r") as file:
        config: list[ExecConfig] = []
        for item in yaml.load(file.read(), yaml.CLoader):
            if not item.get("name", None):
                item["name"] = item["file"]

            if item.get("out", None):
                item["out"] = Path(item["out"])
            else:
                item["out"] = Path(item["file"].rstrip(".py"))

            config.append(ExecConfig(**item))

    exec_examples(config)


main()
