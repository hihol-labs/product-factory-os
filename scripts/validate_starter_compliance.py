#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate project scaffold against .pfo-starter.json.")
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    starter_path = project / ".pfo-starter.json"
    if not starter_path.is_file():
        fail(f"missing starter marker: {starter_path}")
    starter = json.loads(starter_path.read_text(encoding="utf-8"))

    for folder in starter.get("folders", []):
        if not (project / folder).is_dir():
            fail(f"starter folder missing: {folder}")
    if not (project / ".env.example").is_file():
        fail("missing .env.example")
    if not (project / ".github" / "workflows" / "validate.yml").is_file():
        fail("missing generated CI workflow")
    if not (project / "justfile").is_file():
        fail("missing generated justfile")

    required = starter.get("requiredArtifacts", [])
    missing_docs = [item for item in required if not (project / item).exists()]
    if missing_docs:
        print("WARNING: required PFO artifacts not created yet: " + ", ".join(missing_docs))

    print(f"OK: starter compliance passed for {project}")


if __name__ == "__main__":
    main()

