#!/usr/bin/env python3
from pathlib import Path


def main() -> None:
    cwd = Path.cwd()
    docs = [
        "DISCOVERY.md",
        "MARKET_BRIEF.md",
        "ICP.md",
        "PRD.md",
        "PRODUCT_BLUEPRINT.md",
        "PROJECT_ARCHITECTURE.md",
        "BUILD_PLAN.md",
        "EXECUTION_GRAPH.md",
        "TEST_PLAN.md",
        "QUALITY_GATES.md",
        "IMPLEMENTATION_PLAN.md",
        "CODEX.md",
    ]
    found = [name for name in docs if (cwd / name).exists()]
    memory = cwd / ".codex-memory" / "MEMORY.md"
    state = cwd / ".codex-memory" / "STATE.json"
    pfo_contracts = [
        ".pfo/PROJECT_CONTRACT.md",
        ".pfo/DATA_POLICY.md",
        ".pfo/GOLDEN_FLOWS.md",
        ".pfo/FORBIDDEN_CHANGES.md",
        ".pfo/FALLBACK_POLICY.md",
        ".pfo/SCOPE_LOCK.md",
    ]
    contracts_found = [name for name in pfo_contracts if (cwd / name).exists()]

    if found:
        print("Product Factory OS docs found: " + ", ".join(found))
    else:
        print("Product Factory OS docs found: none")

    if memory.exists():
        print("Memory index: .codex-memory/MEMORY.md")
    else:
        print("Memory index: none")
    if state.exists():
        print("State file: .codex-memory/STATE.json")
    else:
        print("State file: none")
    if contracts_found:
        print("PFO contracts found: " + ", ".join(contracts_found))
    else:
        print("PFO contracts found: none")


if __name__ == "__main__":
    main()
