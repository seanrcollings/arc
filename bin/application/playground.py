import json
import os
from pathlib import Path

import httpx

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
            if item.get("exec"):
                pl["suggestions"] = (
                    [item["exec"]] if isinstance(item["exec"], str) else item["exec"]
                )
            else:
                pl["suggestions"] = []

            if "--help" not in pl["suggestions"]:
                pl["suggestions"].append("--help")

            print(f"{item['file']} -> {pl['slug']}")

            examples.append(pl)

    return examples


def update_gist(examples: list[dict]):
    token = os.getenv("GITHUB_API_TOKEN")
    httpx.patch(
        "https://api.github.com/gists/c314336f9ddf2c95144412121203a17c",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        json={
            "description": "Playground examples for Arc",
            "files": {"arc-examples.json": {"content": json.dumps(examples, indent=2)}},
        },
    ).raise_for_status()


def update_playground():
    config = get_examples(DOCS_DIR / "examples.json")
    update_gist(config)
