#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$ROOT/scripts/validate_structure.py"
python3 "$ROOT/scripts/validate_runtime.py"

echo "Product Factory OS installed at $ROOT"
