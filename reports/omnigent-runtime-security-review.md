# Security Review: Omnigent-Inspired PFO Runtime

## Scope

Reviewed the local-first PFO runtime additions for agent YAML specs, policy verdicts, dispatch envelopes, cross-harness review, cost/risk routing, session export/import, live status, and sandbox specification.

## Threat Model

The primary risks are unsafe tool escalation, accidental external execution, broad filesystem writes, misleading policy success, sensitive state leakage in exported session packets, and review bypass for high-risk diffs.

## Discovery

The review covered `scripts/pfo.py`, `docs/templates/PFO_AGENT_SPEC.yaml`, `agents/*.yaml`, `docs/templates/UNIT_CONTEXT_MANIFEST.json`, `docs/templates/pfo/UNIT_CONTEXT_MANIFEST.json`, `docs/templates/pfo/PERMISSION_MATRIX.json`, `docs/PFO_OMNIGENT_RUNTIME.md`, and `scripts/validate_omnigent_runtime.py`.

## Validation

Validation focused on fail-closed behavior, bounded local artifacts, absence of automatic external agent launch, explicit `ALLOW` / `DENY` / `ASK` verdicts, different-harness review enforcement, and sandbox fields in both agent and unit specs.

## Attack Path

Potential attack paths considered: policy downgrade through permissive defaults, dispatch metadata interpreted as authorization to mutate production, session export leaking secrets, and fake cross-review using the same harness. The implementation records envelopes and decisions but does not grant external writes, production mutation, secret reads, or automatic merge authority.

## Findings

### No findings

No Critical or High findings were identified in this implementation. Remaining risk is operational: future hosted or real sub-agent execution must continue to route through the same permission matrix and policy verdict layer.

## Coverage Artifacts

- `reports/omnigent-runtime-security/deep_review_input.csv`
- `reports/omnigent-runtime-security/work_ledger.jsonl`
- `reports/omnigent-runtime-security/repository_coverage_ledger.md`
- `reports/omnigent-runtime-security/candidate_ledger.jsonl`

## Final Decision

PASSED_WITH_WARNINGS. The runtime layer is acceptable for local-first PFO use because it adds guide/sensor controls without enabling uncontrolled external execution. Hosted runner or managed sandbox work must receive a separate security review before release.
