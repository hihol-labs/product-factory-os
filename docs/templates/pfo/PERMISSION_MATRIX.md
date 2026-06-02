# Permission Matrix

Purpose: define who or what may read, write, execute, publish, and touch external systems.

Machine-readable source: `.pfo/PERMISSION_MATRIX.json`.

| Capability | Default | Agent | User Approval Required | Evidence |
|---|---|---|---|---|
| Read project files | Allow | Codex | No | Referenced files in response/state |
| Write project files | Scoped | Codex | When outside `.pfo/UNIT_CONTEXT_MANIFEST.json` | Diff plus manifest |
| Run local verification | Allow when declared | Codex | No | `.codex-memory/events.jsonl` and `verificationHistory` |
| Install dependencies | Block | Codex | Yes | Approval plus command log |
| Read secrets | Block | Codex | Yes | Approval plus reason |
| External API read | Scoped | Codex | When private/sensitive | Connector/tool event |
| External API write | Block | Codex | Yes | Approval plus event |
| Git commit | Scoped | Codex | When requested or approved | Commit hash/event |
| Git push | Block | Codex | Yes | Remote branch/event |
| Context budget | Allow when declared | Codex | No | `.codex-memory/context-index.json`, `.codex-memory/resume-snapshot.md`, event |
| Deploy or migrate production | Block | Codex | Yes | Rollback, checks, approval, event |

Rules:

- Project-local rules may tighten this matrix, but must not make production or external writes implicit.
- Any permission exception must be recorded in `.codex-memory/events.jsonl`.
- Dangerous routes must use the smallest approved command surface.
- Large tool/read/log/web/raw HTTP output must pass `pfo context-budget` or be routed through sandbox-summary before it enters active chat context.
