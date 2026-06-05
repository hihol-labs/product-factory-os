#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str], cwd: Path = ROOT) -> None:
    print(f"==> {label}: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def smoke_project() -> None:
    with tempfile.TemporaryDirectory(prefix="pfo-root-check-") as tmp:
        workspace = Path(tmp)
        project = workspace / "smoke-pfo-product"
        run(
            "bootstrap smoke project",
            [sys.executable, "scripts/pfo_new_project.py", "smoke-pfo-product", "--workspace", str(workspace), "--idea", "Root check smoke"],
        )
        run("plan smoke project", [sys.executable, "scripts/pfo.py", "plan", str(project), "--note", "root check smoke"])
        run("validate smoke state", [sys.executable, "scripts/validate_state.py", str(project / ".codex-memory" / "STATE.json")])
        run("validate smoke project", [sys.executable, "scripts/validate_project.py", str(project)])
        run("analyze smoke project", [sys.executable, "scripts/pfo.py", "analyze", str(project), "--report"])
        run("report smoke project", [sys.executable, "scripts/pfo_report.py", str(project)])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the root Product Factory OS check command.")
    parser.add_argument("--no-smoke", action="store_true", help="Skip temporary generated-project smoke checks.")
    args = parser.parse_args()

    run("compile runtime CLI", [sys.executable, "-m", "py_compile", "scripts/pfo.py", "scripts/existing_project_analyzer.py"])
    run("production readiness", [sys.executable, "scripts/production_readiness.py"])
    if not args.no_smoke:
        smoke_project()
    print("OK: root PFO check passed")


if __name__ == "__main__":
    main()
