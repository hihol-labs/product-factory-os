# Quality Gates

## Gate Results

| Gate | Status | Evidence | Blockers |
|---|---|---|---|
| Idea Gate |  | `IDEA_SCORECARD.md` KILL/TEST/BUILD decision |  |
| Market Validation |  | `VALIDATION_PLAN.md` experiments and signals |  |
| Strategy |  |  |  |
| Feedback Loop |  | `FEEDBACK_LOG.md`, `ITERATION_REVIEW.md` |  |
| Funnel |  | `FUNNEL_MODEL.md` metrics or not-applicable note |  |
| Architecture |  |  |  |
| Tests |  |  |  |
| Review |  |  |  |
| TDD Red |  | failing test command and expected failure |  |
| TDD Green |  | passing test command after minimal implementation |  |
| TDD Refactor |  | post-refactor passing command or not-applicable note |  |
| Root Cause |  | `ROOT_CAUSE.md` for bugfixes |  |
| Spec Compliance Review |  | unit output checked against manifest/spec |  |
| Code Quality Review |  | maintainability, simplicity, integration checks |  |
| Unit Context Manifest |  | `.pfo/UNIT_CONTEXT_MANIFEST.json` |  |
| Execution Policy |  | `.pfo/EXECUTION_POLICY.json` |  |
| Permission Matrix |  | `.pfo/PERMISSION_MATRIX.json`, `.pfo/PERMISSION_MATRIX.md`, `pfo permission-check` |  |
| Verification Contract |  | `.pfo/VERIFICATION_CONTRACT.json` |  |
| Tool Capability Registry |  | `.pfo/TOOL_CAPABILITY_REGISTRY.json`, `pfo tool-registry` |  |
| Control Harness Feedforward |  | active instructions, contracts, scope, and verification expectations are named before work starts |  |
| Control Harness Computational Feedback |  | deterministic checks: tests, validators, CI, schema, build, or contract gate |  |
| Control Harness Inferential Feedback |  | reviewer/security/UX/human judgment evidence when semantic risk exists |  |
| Handoff |  | `HANDOFF.md` before session transfer, role switch, delegation, AFK, compaction, or recovery |  |
| Work Verification |  | verification log / command output |  |
| Experiment Loop |  | `.pfo/EXPERIMENT_PROGRAM.md`, `.pfo/EXPERIMENTS.tsv`, fixed metric and keep/discard/crash decision |  |
| Browser Smoke |  | `/browser-check` target, engine, flow, screenshot/log evidence for browser-facing products |  |
| Security |  |  |  |
| Dependencies |  |  |  |
| Hardening |  |  |  |
| Scope Lock |  | `.pfo/SCOPE_LOCK.md`, diff review |  |
| Data Authenticity |  | `.pfo/DATA_POLICY.md`, data-source evidence |  |
| Golden Flows |  | `.pfo/GOLDEN_FLOWS.md`, tests/manual verification |  |
| Regression Contract |  | `.pfo/PROJECT_CONTRACT.md`, behavior checks |  |
| Fallback Policy |  | `.pfo/FALLBACK_POLICY.md`, degraded-mode checks |  |
| Diff Risk |  | `PFO_CONTRACT_GATE.json` |  |
| No Silent Substitution |  | diff scan, project contracts |  |
| Deployment Readiness |  |  |  |
| Branch Finish |  | PR/merge/keep/discard decision with verification |  |
| Learning Extraction |  | `.codex-memory/LEARNINGS.md` when applicable |  |
| Learning Promotion |  | `.pfo/LEARNING_PROMOTION_GATE.md`, `.codex-memory/LEARNING_PROPOSALS.json` |  |
| Asset Extraction |  | `ASSET_REGISTER.md` when applicable |  |
| Content Pipeline |  | `CONTENT_BACKLOG.md` when applicable |  |

## Accepted Risks

## Next Gate
