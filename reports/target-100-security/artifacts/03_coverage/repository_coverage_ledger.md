# Repository Coverage Ledger

| ID | Path | Risk checked | Result |
| --- | --- | --- | --- |
| target-100-001 | `scripts/pfo_metrics.py` | False PASS for sub-target metrics | No issue found; live eval blocks <=95% verification pass rate and >=0.25 repair loops. |
| target-100-002 | `scripts/validate_workspace_targets.py` | Missing deterministic target gate | No issue found; validator exits non-zero for missed targets. |
| target-100-003 | `scripts/production_readiness.py` | Readiness bypass | No issue found; target validator is wired into readiness. |
| target-100-004 | `scripts/release_check.py` | Release bypass | No issue found; live proof remains mandatory and target validator is wired after it. |
| target-100-005 | `scripts/install_workspace.py` | Global auto-adoption ambiguity | No issue found; policy explicitly covers new and existing projects anywhere on the computer. |
| target-100-006 | `scripts/pfo_contract_gate.py` | False dependency risk | No issue found; dependency matching uses changed manifest and lockfile paths. |
| target-100-007 | `reports/target-100-workspace-metrics.json` | Secret leakage in CI proof | No issue found; artifact contains aggregate ratios and status only. |
| target-100-008 | `dashboard/index.html` | Unsafe metrics rendering | No issue found; values are rendered through existing escaped metric helpers. |
