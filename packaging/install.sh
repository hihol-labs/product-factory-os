#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="$(dirname "$ROOT")"
INSTALL_HOOKS=1
ADOPT_WORKSPACE=1
INSTALL_BIN=1
WRITE_WORKSPACE_POLICY=1
SKIP_CHECKS=0

usage() {
  cat <<'EOF'
Usage: bash install.sh [options]

Installs Product Factory OS as the default Codex runtime for a workspace.

Options:
  --workspace PATH       Workspace used by PFO commands. Default: parent of repo.
  --install-hooks        Kept for compatibility; hooks are installed by default.
  --no-hooks             Do not install hooks.
  --no-adopt             Do not adopt existing first-level workspace projects.
  --no-bin               Do not install the pfo command wrapper into ~/.local/bin.
  --no-workspace-policy  Do not write workspace CODEX.md, AGENTS.md, and PFO_WORKSPACE.json.
  --skip-checks          Skip validation checks.
  -h, --help          Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE="$2"
      shift 2
      ;;
    --install-hooks)
      INSTALL_HOOKS=1
      shift
      ;;
    --no-hooks)
      INSTALL_HOOKS=0
      shift
      ;;
    --no-adopt)
      ADOPT_WORKSPACE=0
      shift
      ;;
    --no-bin)
      INSTALL_BIN=0
      shift
      ;;
    --no-workspace-policy)
      WRITE_WORKSPACE_POLICY=0
      shift
      ;;
    --skip-checks)
      SKIP_CHECKS=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ "$SKIP_CHECKS" -eq 0 ]]; then
  python3 "$ROOT/scripts/validate_structure.py"
  python3 "$ROOT/scripts/run_fixtures.py"
  python3 "$ROOT/scripts/validate_runtime.py"
  python3 "$ROOT/scripts/validate_hooks.py"
fi

INSTALL_ARGS=(--workspace "$WORKSPACE")
if [[ "$INSTALL_HOOKS" -eq 0 ]]; then
  INSTALL_ARGS+=(--no-hooks)
fi
if [[ "$ADOPT_WORKSPACE" -eq 0 ]]; then
  INSTALL_ARGS+=(--no-adopt)
fi
if [[ "$INSTALL_BIN" -eq 0 ]]; then
  INSTALL_ARGS+=(--no-bin)
fi
if [[ "$WRITE_WORKSPACE_POLICY" -eq 0 ]]; then
  INSTALL_ARGS+=(--no-workspace-policy)
fi

python3 "$ROOT/scripts/install_workspace.py" "${INSTALL_ARGS[@]}"
