import json
import os
from pathlib import Path
import github


ROOT_DIR = Path(".")
DOCS_DIR = ROOT_DIR / "docs"
EXAMPLE_DIR = DOCS_DIR / "examples"
OUTPUT_DIR = EXAMPLE_DIR / "outputs"


def get_examples(file) -> list[dict]:
    examples: list[dict] = []
    with open(file, "r") as f:
        item: dict
        for item in json.loads(f.read()):
            if not item.get("playground"):
                continue

            pl = item["playground"]
            pl["slug"] = item["file"].replace(".py", "").replace("_", "-")
            pl["file"] = item["file"]
            print(f"{item['file']} -> {pl['slug']}")

            examples.append(pl)

    return examples


def update_gist(examples: list[dict]):
    api = github.Github(os.getenv("GITHUB_API_TOKEN"))
    gist = api.get_gist("c314336f9ddf2c95144412121203a17c")
    gist.edit(
        description="Playground examples for Arc",
        files={
            "arc-examples.json": github.InputFileContent(json.dumps(examples, indent=2))
        },
    )


def update_playground():
    config = get_examples(DOCS_DIR / "examples.json")
    update_gist(config)
