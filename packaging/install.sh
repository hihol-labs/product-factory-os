#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="$(dirname "$ROOT")"
INSTALL_HOOKS=0
SKIP_CHECKS=0

usage() {
  cat <<'EOF'
Usage: bash packaging/install.sh [options]

Options:
  --workspace PATH    Workspace used by PFO commands. Default: parent of repo.
  --install-hooks     Copy hook scripts to ${CODEX_HOME:-$HOME/.codex}/hooks/product-factory-os.
  --skip-checks       Skip validation checks.
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

if [[ "$INSTALL_HOOKS" -eq 1 ]]; then
  CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
  HOOK_TARGET="$CODEX_HOME_DIR/hooks/product-factory-os"
  mkdir -p "$HOOK_TARGET"
  cp "$ROOT/hooks/"*.py "$HOOK_TARGET/"
  cp "$ROOT/hooks/hooks.json" "$HOOK_TARGET/hooks.json"
  chmod +x "$HOOK_TARGET/"*.py
  echo "Installed PFO hooks into $HOOK_TARGET"
  echo "Register hooks explicitly from hooks/hooks.json if your Codex build requires manual hook registration."
fi

echo "Product Factory OS repository: $ROOT"
echo "Workspace: $WORKSPACE"
echo "Smoke test:"
echo "  python3 $ROOT/scripts/pfo.py new smoke-product --workspace /tmp --idea \"Smoke SaaS product\""
echo "  python3 $ROOT/scripts/pfo.py plan /tmp/smoke-product"
