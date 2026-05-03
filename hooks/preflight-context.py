#!/usr/bin/env python3
from pathlib import Path


def main() -> None:
    cwd = Path.cwd()
    docs = [
        "DISCOVERY.md",
        "PRD.md",
        "PROJECT_ARCHITECTURE.md",
        "IMPLEMENTATION_PLAN.md",
        "CODEX.md",
    ]
    found = [name for name in docs if (cwd / name).exists()]
    memory = cwd / ".codex-memory" / "MEMORY.md"

    if found:
        print("Product Factory OS docs found: " + ", ".join(found))
    else:
        print("Product Factory OS docs found: none")

    if memory.exists():
        print("Memory index: .codex-memory/MEMORY.md")
    else:
        print("Memory index: none")


if __name__ == "__main__":
    main()

