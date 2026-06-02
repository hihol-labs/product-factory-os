# Repository Coverage Ledger

| Row | Surface | Risk Area | Outcome | Notes |
|---|---|---|---|---|
| security-audit-v2-001 | `/security-audit` skill | incomplete security workflow | No issue found | Phase separation and coverage artifacts are required. |
| security-audit-v2-002 | `pfo_contract_gate.py` | unreviewed `security_change` diff | No issue found | Gate blocks without Codex Security or PFO-equivalent evidence. |
| security-audit-v2-003 | `validate_security_report.py` | weak report shape | No issue found | Report sections, finding fields, and remediation are validated. |
| security-audit-v2-004 | `/bugfix` skill | security fix without reproduction | No issue found | Fix-finding path requires reproduction and closure proof. |
| security-audit-v2-005 | security rubric and docs | undocumented blocker semantics | No issue found | Rubric/gate docs define artifacts and statuses. |
