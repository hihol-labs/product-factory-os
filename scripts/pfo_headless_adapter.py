#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import shlex
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def env_path(name: str) -> Path:
    value = os.environ.get(name)
    if not value:
        fail(f"{name} is required")
    return Path(value)


def build_prompt(fixture: str, prompt_file: Path, output_dir: Path, contract: dict) -> str:
    return f"""You are running a Product Factory OS headless behavioural fixture.

Fixture: {fixture}
Prompt file: {prompt_file}
Output directory: {output_dir}

Rules:
- Read the user request below.
- Generate the required PFO result for this fixture.
- Write artifacts only under the output directory.
- Do not write outside the output directory.
- Do not ask follow-up questions; use conservative assumptions and record them.
- If the contract expects stdout-only output, do not create files.
- If blocked, explain the blocker and exit without claiming success.

Behavioural output contract:
```json
{json.dumps(contract.get("output_contract", {}), indent=2, ensure_ascii=False)}
```

User request:
```markdown
{prompt_file.read_text(encoding="utf-8")}
```
"""


def subprocess_env(args: argparse.Namespace) -> dict[str, str]:
    env = os.environ.copy()
    if args.clear_proxy_env:
        for key in [
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "FTP_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
            "ftp_proxy",
        ]:
            env.pop(key, None)
    return env


def run_codex(prompt: str, output_dir: Path, args: argparse.Namespace) -> int:
    last_message = output_dir / ".pfo-headless-last-message.txt"
    command = [
        "codex",
        "exec",
        "-C",
        str(output_dir),
        "--sandbox",
        "workspace-write",
        "--skip-git-repo-check",
        "--ephemeral",
        "--output-last-message",
        str(last_message),
        "-",
    ]
    if args.model:
        command.extend(["--model", args.model])
    if args.dry_run:
        print(shlex.join(command) + " < prompt")
        return 0
    result = subprocess.run(
        command,
        input=prompt,
        text=True,
        capture_output=True,
        cwd=output_dir,
        env=subprocess_env(args),
        check=False,
    )
    if last_message.is_file():
        print(last_message.read_text(encoding="utf-8"), end="")
        last_message.unlink()
    else:
        print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Codex adapter for real PFO headless fixture execution.")
    parser.add_argument("--model", default=os.environ.get("PFO_HEADLESS_MODEL"))
    parser.add_argument("--clear-proxy-env", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    fixture = os.environ.get("PFO_FIXTURE")
    if not fixture:
        fail("PFO_FIXTURE is required")
    prompt_file = env_path("PFO_PROMPT_FILE")
    output_dir = env_path("PFO_OUTPUT_DIR")
    output_dir.mkdir(parents=True, exist_ok=True)

    registry = json.loads((ROOT / "tests" / "fixture-contracts.json").read_text(encoding="utf-8"))
    contract = registry.get("fixtures", {}).get(fixture)
    if not contract:
        fail(f"missing fixture contract for {fixture}")

    prompt = build_prompt(fixture, prompt_file, output_dir, contract)
    raise SystemExit(run_codex(prompt, output_dir, args))


if __name__ == "__main__":
    main()
