#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
from html import escape
import json
import re
import subprocess
import sys

from pfo_alias_targets import missing_targets_for_text

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
ALIAS_DOCUMENT_NAMES = [
    "MASTER_CONTEXT.md",
    "ARCHITECTURE.md",
    "TASKS.md",
    "PROGRESS.md",
    "TESTING.md",
]


def load_alias_documents() -> dict[str, str]:
    return {
        name: (ROOT / "docs" / "templates" / name).read_text(encoding="utf-8")
        for name in ALIAS_DOCUMENT_NAMES
    }


def run_script(name: str, args: list[str]) -> int:
    command = [sys.executable, str(ROOT / "scripts" / name), *args]
    return subprocess.run(command, cwd=ROOT).returncode


def load_state(project: Path) -> dict:
    state_path = project / ".codex-memory" / "STATE.json"
    if not state_path.is_file():
        raise SystemExit(f"ERROR: missing state file: {state_path}")
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(project: Path, state: dict) -> None:
    state_path = project / ".codex-memory" / "STATE.json"
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_event(project: Path, state: dict, event_type: str, status: str, payload: dict, source: str = "pfo-cli") -> None:
    timestamp = now_iso()
    event_id = f"event-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{len(state.get('dispatchJournal', [])) + 1}"
    event = {
        "id": event_id,
        "timestamp": timestamp,
        "eventType": event_type,
        "status": status,
        "project": project.name,
        "source": source,
        "payload": payload,
    }
    event_path = project / ".codex-memory" / "events.jsonl"
    event_path.parent.mkdir(parents=True, exist_ok=True)
    with event_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    state["eventLog"] = {
        "path": ".codex-memory/events.jsonl",
        "lastEventId": event_id,
        "lastEventAt": timestamp,
    }
    add_artifact(state, ".codex-memory/events.jsonl")


def add_artifact(state: dict, artifact: str) -> None:
    artifacts = set(state.get("artifacts", []))
    artifacts.add(artifact)
    state["artifacts"] = sorted(artifacts)


def default_human_steering() -> dict:
    return {
        "approvalRequired": True,
        "approvalStatus": "PENDING",
        "approvedBy": "",
        "approvedAt": "",
        "lastPrompt": "Ask the user to confirm, change, or stop before implementation.",
        "lastIterationSummary": "PFO runtime is active and waiting for next-step steering.",
        "recommendedNextStep": "Choose and approve the next task-specific implementation step.",
        "alternatives": [
            "Approve the recommended next step.",
            "Change scope or priority.",
            "Pause and review the plan."
        ],
        "pendingQuestions": [
            "Do you approve the recommended next step?",
            "Should scope or priority change before implementation?"
        ],
        "visibleRoadmap": [],
        "completedIterations": [],
    }


def ensure_human_steering(state: dict) -> dict:
    steering = state.setdefault("humanSteering", default_human_steering())
    if not isinstance(steering, dict):
        steering = default_human_steering()
        state["humanSteering"] = steering
    for key, value in default_human_steering().items():
        steering.setdefault(key, value)
    if not steering.get("approvalStatus"):
        steering["approvalStatus"] = "PENDING"
    if steering.get("approvalStatus") == "PENDING":
        steering["approvalRequired"] = True
    if not steering.get("recommendedNextStep"):
        steering["recommendedNextStep"] = default_human_steering()["recommendedNextStep"]
    gates = state.setdefault("gateResults", {})
    gates.setdefault("nextStepApproval", "PENDING")
    if not gates.get("nextStepApproval"):
        gates["nextStepApproval"] = "PENDING"
    return steering


def ensure_autonomy_state(state: dict) -> None:
    state.setdefault("currentPhase", "")
    state.setdefault(
        "currentUnit",
        {"id": "", "goal": "", "status": "", "owner": "", "startedAt": "", "completedAt": ""},
    )
    state.setdefault(
        "unitContextManifest",
        {
            "path": ".pfo/UNIT_CONTEXT_MANIFEST.json",
            "version": 1,
            "unitId": "",
            "requiredInputs": [],
            "allowedWriteAreas": [],
            "forbiddenChanges": [],
            "dependencies": [],
            "verificationCommands": [],
            "gates": [],
            "pivLoop": {
                "planPath": "plans/unit-piv-plan.md",
                "implementationReportPath": "reports/unit-implementation-report.md",
                "sequence": ["plan", "implement", "validate", "review"],
            },
            "engineeringDiscipline": {
                "behaviorChange": False,
                "bugfix": False,
                "strictPlan": True,
                "requiresTdd": "behavior changes",
                "requiresRootCause": "bugfix units",
            },
            "recovery": "",
        },
    )
    state.setdefault(
        "handoff",
        {
            "path": "HANDOFF.md",
            "status": "",
            "fromRole": "",
            "toRole": "",
            "reason": "",
            "createdAt": "",
            "nextAction": "",
        },
    )
    state.setdefault("dispatchJournal", [])
    state.setdefault("capturedNotes", [])
    state.setdefault("tddEvidence", {"red": "", "green": "", "refactor": "", "lastRecordedAt": ""})
    state.setdefault(
        "rootCause",
        {"status": "", "summary": "", "evidence": "", "hypothesis": "", "recordedAt": ""},
    )
    state.setdefault(
        "reviewStages",
        {
            "specCompliance": {"status": "", "evidence": "", "recordedAt": ""},
            "codeQuality": {"status": "", "evidence": "", "recordedAt": ""},
        },
    )
    state.setdefault(
        "branchFinish",
        {
            "status": "",
            "mode": "",
            "verification": "",
            "remoteBranch": "",
            "prUrl": "",
            "cleanupDecision": "",
            "recordedAt": "",
        },
    )
    state.setdefault("driftChecks", [])
    state.setdefault("knowledgeLog", [])
    state.setdefault("learningProposals", [])
    state.setdefault("eventLog", {"path": ".codex-memory/events.jsonl", "lastEventId": "", "lastEventAt": ""})
    state.setdefault("executionPolicy", {"path": ".pfo/EXECUTION_POLICY.json", "status": ""})
    state.setdefault("permissionMatrix", {"path": ".pfo/PERMISSION_MATRIX.json", "humanPath": ".pfo/PERMISSION_MATRIX.md", "status": ""})
    state.setdefault("verificationContract", {"path": ".pfo/VERIFICATION_CONTRACT.json", "status": ""})
    state.setdefault("toolCapabilityRegistry", {"path": ".pfo/TOOL_CAPABILITY_REGISTRY.json", "status": ""})
    state.setdefault("learningPromotionGate", {"path": ".pfo/LEARNING_PROMOTION_GATE.md", "status": ""})
    state.setdefault(
        "experimentLoop",
        {
            "status": "",
            "tag": "",
            "programPath": ".pfo/EXPERIMENT_PROGRAM.md",
            "resultsPath": ".pfo/EXPERIMENTS.tsv",
            "metric": {"name": "", "direction": "lower", "bestValue": None, "bestRunId": ""},
            "budgetSeconds": None,
            "runCommand": "",
            "baselineCommand": "",
            "allowedWriteAreas": [],
            "protectedFiles": [],
            "baselineRecorded": False,
            "lastRun": {},
        },
    )
    state.setdefault("briefArtifacts", [])
    state.setdefault(
        "recoveryState",
        {"status": "", "reason": "", "retryCount": 0, "nextRepairAction": ""},
    )
    state.setdefault(
        "telemetry",
        {
            "unitCount": 0,
            "verificationCount": 0,
            "lastCommand": "",
            "lastDurationSeconds": None,
            "tokenNotes": "",
            "costNotes": "",
        },
    )
    state.setdefault(
        "worktreeIsolation",
        {"enabled": False, "strategy": "", "activeBranch": "", "activeWorktree": "", "mergeStatus": ""},
    )
    gates = state.setdefault("gateResults", {})
    for gate in [
        "ideaGate",
        "marketValidation",
        "feedbackLoop",
        "funnel",
        "tddRed",
        "tddGreen",
        "tddRefactor",
        "rootCause",
        "specComplianceReview",
        "codeQualityReview",
        "branchFinish",
        "nextStepApproval",
        "handoff",
        "assetExtraction",
        "contentPipeline",
        "experimentSetup",
        "experimentMetric",
        "experimentDecision",
        "executionPolicy",
        "permissionMatrix",
        "verificationContract",
        "learningPromotion",
        "toolCapabilityRegistry",
    ]:
        gates.setdefault(gate, "")
    ensure_human_steering(state)


def load_starter(project: Path, state: dict) -> dict:
    starter_path = project / ".pfo-starter.json"
    if starter_path.is_file():
        return json.loads(starter_path.read_text(encoding="utf-8"))
    starter_id = state.get("starter") or "saas-fastapi-vue"
    starter_file = ROOT / "starters" / starter_id / "STARTER.json"
    if starter_file.is_file():
        return json.loads(starter_file.read_text(encoding="utf-8"))
    return {
        "id": "custom",
        "productType": state.get("productTypeHint", "web_app"),
        "stack": [],
        "folders": [],
        "commands": {},
        "requiredArtifacts": [],
    }


def write_if_missing(path: Path, text: str) -> bool:
    if path.exists():
        return False
    path.write_text(text, encoding="utf-8")
    return True


def write_alias_documents(project: Path) -> list[str]:
    written = []
    for name, text in load_alias_documents().items():
        errors = missing_targets_for_text(project, name, text)
        if errors:
            raise SystemExit("ERROR: refusing to create alias document with missing target(s):\n" + "\n".join(f"- {item}" for item in errors))
        if write_if_missing(project / name, text):
            written.append(name)
    return written


def generated_blueprint(project: Path, state: dict, starter: dict) -> str:
    idea = state.get("intent") or "Product idea not captured yet."
    product_type = starter.get("productType") or state.get("productTypeHint") or ""
    stack = ", ".join(starter.get("stack", [])) or "project-specific stack"
    stack_preset = starter.get("stackPreset") or "pfo-default-stack-v1"
    modules = starter.get("folders", [])
    module_rows = "\n".join(
        f"| {folder} | Runtime area generated by starter `{starter.get('id', 'custom')}` | TBD | starter contract |"
        for folder in modules[:8]
    ) or "| core | Product runtime core | TBD | custom contract |"
    return f"""# Product Blueprint

## Product Classification

```text
PRODUCT_TYPE: {product_type}
DOMAIN: TBD from discovery
COMPLEXITY: TBD
REQUIRED_MODULES: {', '.join(modules) if modules else 'TBD'}
INFRASTRUCTURE: {stack}
STACK_PRESET: {stack_preset}
STACK_DEVIATION_POLICY: Document reason, risk, support cost, and verification impact in PROJECT_ARCHITECTURE.md.
```

## Initial Intent

{idea}

## Business Logic

Describe the smallest useful value loop before implementation.

## Users And Roles

- Primary user: TBD
- Operator/admin: TBD

## Core Entities

| Entity | Purpose | Fields | Relationships |
|---|---|---|---|
| User | Person or account using the product | id, contact, status | owns product actions |
| Work Item | Main product object | id, state, timestamps | belongs to user |

## Modules

| Module | Responsibility | Depends On | Template Contract |
|---|---|---|---|
{module_rows}

## Interfaces

- Pages: TBD
- API: TBD
- Commands: TBD
- Bot handlers: TBD
- CLI commands: TBD

## Infrastructure

- Runtime: {stack}
- Database: TBD
- Queue: TBD
- Storage: TBD
- Deployment target: TBD

## Risks And Assumptions

- Validate unclear requirements before writing production behavior.
- Keep `.pfo/` contracts authoritative for scope, data, fallback, and golden-flow rules.
"""


def generated_architecture(starter: dict) -> str:
    stack = ", ".join(starter.get("stack", [])) or "TBD"
    stack_preset = starter.get("stackPreset") or "pfo-default-stack-v1"
    commands = starter.get("commands", {})
    command_rows = "\n".join(f"- `{name}`: `{command}`" for name, command in commands.items()) or "- TBD"
    return f"""# PROJECT_ARCHITECTURE

## Stack

{stack}

## Stack Preset

- Default: PFO Default Stack v1
- Selected: {stack_preset}

## Stack Deviations

| Decision | Reason | Risk | Support Cost | Verification Impact |
|---|---|---|---|---|
| None | Starter baseline accepted | Low | Low | Starter commands remain valid |

## Rationale

Use the selected starter `{starter.get('id', 'custom')}` as the initial architecture baseline. Replace defaults only when product requirements require it.

## Data Model

Define entities in `PRODUCT_BLUEPRINT.md`, then turn them into migrations or schema files during the relevant execution graph node.

## API, Pages, Commands, Or Handlers

TBD by product interface.

## Auth And Permissions

Start with least privilege. Add auth only when the product flow requires persistent users, private data, payments, admin operations, or integrations.

## Integrations

TBD.

## Deployment Topology

Use generated CI and starter commands first:

{command_rows}

## Observability

Add health checks, structured logs, and error reporting before `READY_FOR_DEPLOY`.

## Risks And Tradeoffs

- Starter defaults are scaffolding, not final product truth.
- Deployment is blocked until tests, review, security, dependency, hardening, and `.pfo/` contract gates are explicit.
"""


def generated_build_plan(starter: dict) -> str:
    commands = starter.get("commands", {})
    test_command = commands.get("backendTest") or commands.get("frontendTest") or "project test command"
    build_command = commands.get("build") or "project build command"
    return f"""# Build Plan

## Module Order

| Step | Module | Dependencies | Files Likely Touched | Verification | Exit Criteria |
|---:|---|---|---|---|---|
| 1 | Starter baseline and contracts | CODEX.md, `.pfo/` | starter files, `.env.example`, CI | `python3 scripts/pfo.py validate <project>` | project validates under PFO |
| 2 | Idea and validation gate | initial intent | IDEA_SCORECARD.md, VALIDATION_PLAN.md | review scorecard decision | weak ideas are killed or narrowed before build |
| 3 | GTM and feedback model | validation plan | GO_TO_MARKET.md, FUNNEL_MODEL.md, FEEDBACK_LOG.md | measurable signal and funnel bottleneck named | market test can be measured |
| 4 | Next-step steering | BUILD_PLAN.md, EXECUTION_GRAPH.md | NEXT_STEP.md | user confirms, changes, or pauses | owner knows what happens next |
| 5 | Phase decisions and unit manifest | PRODUCT_BLUEPRINT.md, PHASE_CONTEXT.md | BUILD_PLAN.md, EXECUTION_GRAPH.md, `.pfo/UNIT_CONTEXT_MANIFEST.json` | `pfo manifest <project>` | execution unit has scoped context |
| 6 | Handoff gate | plan, manifest, state | HANDOFF.md | `pfo handoff <project>` when transfer is needed | next actor can start without chat history |
| 7 | TDD evidence loop | `.pfo/UNIT_CONTEXT_MANIFEST.json` | tests, minimal source files | `pfo tdd-evidence <project> --red ... --green ...` | red and green evidence recorded |
| 8 | Product domain model | PRODUCT_BLUEPRINT.md | backend, database, shared types | `{test_command}` | core entities covered by tests |
| 9 | Primary user flow | domain model | frontend, API, bot, or CLI handlers | smoke path from TEST_PLAN.md | golden flow documented and verified |
| 10 | Feedback-driven iteration | primary flow | FEEDBACK_LOG.md, ITERATION_REVIEW.md | iteration decision recorded | changes are tied to signal, not activity |
| 11 | Asset and content extraction | completed milestone | ASSET_REGISTER.md, CONTENT_BACKLOG.md | reusable asset candidate recorded | repeatable solutions become assets |
| 12 | Two-stage review | implemented unit | review notes, `QUALITY_GATES.md` | `pfo review-stage <project> --stage spec ...` and `--stage quality ...` | spec and code-quality reviews recorded |
| 13 | Quality gates | implemented flow | TEST_PLAN.md, QUALITY_GATES.md | review/security/deps/harden gates | no critical blocker remains |
| 14 | Branch finish | quality gates | branch, PR, merge notes | `pfo finish-branch <project> --mode pr --verification ...` | merge/PR/keep/discard decision explicit |
| 15 | Deploy readiness | quality gates | Docker, CI, docs, rollback notes | `{build_command}` | READY_FOR_DEPLOY can be reached |

## Executable Tasks

Every executable task must include:

- Current idea/validation decision when the task expands product scope.
- Exact files to create or modify.
- Exact verification command.
- Expected output or failure mode.
- User-facing next-step approval in `NEXT_STEP.md` before major implementation starts.
- TDD red and green evidence for behavior changes.
- Root-cause evidence for bugfixes.
- Spec compliance review before code quality review.
- Branch finish decision: PR, merge, keep, or discard.

Do not leave `TBD`, `TODO`, "add tests", "handle errors", or "similar to previous task" placeholders in executable tasks.

## Cross-Module Dependencies

- Implementation order follows `EXECUTION_GRAPH.md`.
- Any change touching a golden flow must update `.pfo/GOLDEN_FLOWS.md` evidence.
- Build scope must follow `IDEA_SCORECARD.md` and `VALIDATION_PLAN.md` decisions.

## Test Strategy

- Use starter commands where available.
- Add focused regression tests for changed behavior.
- Browser-facing products require `/browser-check` before deploy readiness.

## Gate Strategy

- Run `.pfo/` contract gate on every meaningful diff.
- Do not expand implementation from TEST to BUILD without validation evidence.
- Record TDD red/green/refactor evidence for behavior changes.
- Bugfixes require root-cause evidence before the fix.
- Review runs in two stages: spec compliance first, code quality second.
- Deployment requires explicit user confirmation and non-blocked gates.

## Task Granularity

Every execution task must name exact files, exact commands, expected output, and exit criteria. Do not leave `TBD`, `TODO`, "add tests", or "handle errors" placeholders in executable tasks.

## Deferred Work

- Non-MVP modules stay out of scope until `SCOPE_LOCK.md` is updated.
"""


def generated_test_plan(starter: dict) -> str:
    commands = starter.get("commands", {})
    backend = commands.get("backendTest", "TBD")
    frontend = commands.get("frontendTest", "TBD")
    build = commands.get("build", "TBD")
    return f"""# Test Plan

## Product Type

{starter.get('productType', 'TBD')}

## Test Matrix

| Layer | Scope | Command | Required For |
|---|---|---|---|
| Backend | domain logic, API, integrations | `{backend}` | behavior changes |
| Frontend/UI | critical user flows | `{frontend}` | browser-facing changes |
| Browser smoke | primary UI flow, responsive render, form/nav interaction | `/browser-check` with Playwright evidence | deploy readiness for browser-facing products |
| Build | deployable artifact | `{build}` | deploy readiness |
| PFO contracts | scope/data/fallback/golden flows | `python3 scripts/pfo_contract_gate.py <project>` | every meaningful diff |
| TDD evidence | red, green, refactor command evidence | `pfo tdd-evidence <project> --red ... --green ...` | behavior changes |
| Root cause | reproduction, evidence, fix hypothesis | `pfo root-cause <project> --summary ...` | bug fixes |

## TDD Evidence

| Step | Evidence | Command | Status |
|---|---|---|---|
| Red | failing test before implementation | TBD | PENDING |
| Green | passing test after minimal implementation | TBD | PENDING |
| Refactor | passing test after cleanup or explicit not-applicable note | TBD | PENDING |

## Critical Flows

- Define one primary golden flow before implementation.
- Add at least one smoke path that can be verified locally.

## Negative And Edge Cases

- Invalid input.
- Missing external provider.
- Permission boundary.
- Empty or unavailable data source.

## Smoke Path

| Flow | Target URL/File | Engine | Command Or Manual Check | Evidence |
|---|---|---|---|---|
| Primary browser flow | TBD | Playwright via `/browser-check` when browser-facing | TBD | screenshot/log evidence |

## CI Requirements

- Generated CI must run tests, contract gate, and build checks that are available for the starter.
"""


def generated_idea_scorecard(state: dict) -> str:
    idea = state.get("intent") or "Product idea not captured yet."
    return f"""# Idea Scorecard

## Candidate Idea

{idea}

## Target Segment

TBD

## Problem Evidence

TBD

## Evidence Quality Gate

| Check | Evidence | Status |
|---|---|---|
| Real user conversations count | TBD | PENDING |
| Past behavior evidence, not future intent | TBD | PENDING |
| Contradicting evidence found | TBD | PENDING |
| BUILD truth conditions | TBD | PENDING |

## Supporting Evidence

- TBD

## Contradicting Evidence

- TBD

## Score

| Criterion | Score 1-5 | Evidence | Notes |
|---|---:|---|---|
| Pain intensity |  |  |  |
| Segment clarity |  |  |  |
| Urgency |  |  |  |
| Willingness to pay or adopt |  |  |  |
| Audience access |  |  |  |
| Validation speed |  |  |  |
| Build complexity |  |  |  |
| Strategic fit |  |  |  |

## Decision

```text
STATUS: TEST
RATIONALE: Initial idea requires market and user validation before broad build scope.
```

## Weaknesses To Test First

- TBD

## Kill Criteria

- No painful problem evidence from the target segment.
- No realistic path to first users or internal adopters.
- Validation cost is higher than the value of the next decision.

## Next Validation Step

Create or update `VALIDATION_PLAN.md`.
"""


def generated_validation_plan(state: dict) -> str:
    idea = state.get("intent") or "Product idea not captured yet."
    return f"""# Validation Plan

## Core Hypothesis

{idea}

## Evidence Quality Gate

| Check | Minimum Evidence | Actual Evidence | Status |
|---|---|---|---|
| Real user conversations | Count and segment fit are explicit | TBD | PENDING |
| Past behavior evidence | Users describe what they did, bought, used, hacked together, or abandoned | TBD | PENDING |
| Contradicting evidence | Evidence against the hypothesis is recorded | TBD | PENDING |
| BUILD truth conditions | Conditions that must be true before broad build scope are explicit | TBD | PENDING |

## Riskiest Assumptions

| Assumption | Risk | Evidence Needed | Owner | Deadline |
|---|---|---|---|---|
| Target segment has the problem | high | interview, signup, usage, or purchase intent signal | TBD | TBD |
| MVP scope can produce a useful outcome | medium | prototype test or workflow completion signal | TBD | TBD |
| Acquisition path reaches the segment | medium | channel test or direct outreach response | TBD | TBD |

## Customer Discovery Interviews

### Target Interview Profile

TBD

### Question Discipline

- Ask about the last real occurrence, not hypothetical future use.
- Avoid leading questions, solution pitching, and social-desirability prompts.
- Capture exact words when they reveal urgency, workaround, budget, or indifference.

### Forbidden Or Leading Questions

| Question | Why It Is Weak | Replacement |
|---|---|---|
| Would you use this? | Future intent is weak evidence. | Tell me about the last time this problem happened. |

### Five-Interview Debrief

| Batch | Supporting Evidence | Contradicting Evidence | Surprise | Decision |
|---|---|---|---|---|

## Experiments

| Experiment | Method | Expected Signal | Actual Signal | Decision |
|---|---|---|---|---|
| Problem interview | 5 target users | repeated painful problem signal | TBD | TBD |
| Offer test | landing page, message, or direct pitch | lead, reply, or qualified demo request | TBD | TBD |
| Manual concierge test | deliver outcome manually | user completes target workflow | TBD | TBD |

## Market Signals

- Alternatives: TBD
- Search or demand signal: TBD
- Buyer/user quotes: TBD
- Pricing or budget signal: TBD

## Decision Log

| Date | Decision | Evidence | Next Step |
|---|---|---|---|

## Exit Decision

```text
CONTINUE | PIVOT | STOP
```
"""


def generated_feedback_log() -> str:
    return """# Feedback Log

## Sources

| Source | Segment | Channel | Date |
|---|---|---|---|

## Feedback

| Date | User Or Source | Signal | Evidence | Severity | Product Area | Follow-Up |
|---|---|---|---|---|---|---|

## Patterns

TBD

## Open Questions

TBD

## Decisions Triggered

| Decision | Evidence | Artifact To Update |
|---|---|---|
"""


def generated_iteration_review() -> str:
    return """# Iteration Review

## Iteration Window

TBD

## Goal

TBD

## Inputs

- Feedback: `FEEDBACK_LOG.md`
- Metrics: TBD
- Validation evidence: `VALIDATION_PLAN.md`
- Strategic decision: `PHASE_CONTEXT.md` or ADR

## Changes Made

| Change | Reason | Evidence | Verification |
|---|---|---|---|

## Outcome

| Metric Or Signal | Before | After | Interpretation |
|---|---:|---:|---|

## Decision

```text
KEEP | REVERT | ITERATE | PIVOT | STOP
```

## Next Iteration

TBD
"""


def generated_funnel_model() -> str:
    return """# Funnel Model

## Goal

TBD

## Offer

TBD

## MVP Measurement Contract

| Signal | Target | Instrumentation | False Positive To Avoid |
|---|---:|---|---|
| Activation criteria | TBD | TBD | Signups without activation |
| Day 7 retention | TBD | TBD | Launch curiosity without repeat use |
| Day 30 retention | TBD | TBD | Short-term incentive usage |
| Revenue or qualified willingness to pay | TBD | TBD | Compliments without budget |
| Referral or organic pull | TBD | TBD | Founder-driven outreach only |

## PMF Evidence

- Retention: TBD
- Revenue: TBD
- Referral: TBD
- Sean Ellis test: TBD
- Pull vs push signal: TBD

## Funnel Stages

| Stage | User Action | Current Rate | Target Rate | Instrumentation | Bottleneck |
|---|---|---:|---:|---|---|
| Traffic | TBD |  |  | TBD |  |
| Lead | TBD |  |  | TBD |  |
| Activation | TBD |  |  | TBD |  |
| Conversion | TBD |  |  | TBD |  |
| Retention | TBD |  |  | TBD |  |

## Primary Bottleneck

TBD

## Experiment Backlog

| Experiment | Stage | Hypothesis | Metric | Decision |
|---|---|---|---|---|
"""


def generated_asset_register() -> str:
    return """# Asset Register

## Reusable Assets

| Asset | Source | Type | Reuse Target | Owner | Status |
|---|---|---|---|---|---|

## Asset Types

- Product pattern
- Starter module
- Template
- Checklist
- Offer
- Case study
- Research note
- Automation workflow

## Promotion Criteria

- Repeated use or strong evidence.
- Clear owner and scope.
- Documented limitations.
- Verification or example exists.

## Candidates To Promote

TBD
"""


def generated_content_backlog() -> str:
    return """# Content Backlog

## Content Sources

- Decisions from `PHASE_CONTEXT.md`
- Learnings from `.codex-memory/LEARNINGS.md`
- Validation evidence from `VALIDATION_PLAN.md`
- Customer patterns from `FEEDBACK_LOG.md`
- Assets from `ASSET_REGISTER.md`

## Backlog

| Idea | Source Evidence | Format | Audience | Offer Tie-In | Status |
|---|---|---|---|---|---|

## Published Content

| Content | URL Or Location | Source Asset | Result |
|---|---|---|---|

## Rules

- Do not turn private user data into content without explicit approval.
- Tie content to evidence, not internal activity.
- Prefer reusable insights, checklists, teardown notes, and case studies.
"""


def generated_quality_gates() -> str:
    return """# Quality Gates

## Gate Results

| Gate | Status | Evidence | Blockers |
|---|---|---|---|
| Idea Gate | PENDING | IDEA_SCORECARD.md decision is KILL, TEST, or BUILD |  |
| Evidence Quality | PENDING | real user conversations, past behavior evidence, contradicting evidence, BUILD truth conditions |  |
| Adversarial Discovery | PENDING | MARKET_BRIEF.md adversarial discovery answers |  |
| Market Validation | PENDING | VALIDATION_PLAN.md signals and exit decision |  |
| Strategy | PENDING | DISCOVERY.md / MARKET_BRIEF.md when applicable |  |
| Feedback Loop | PENDING | FEEDBACK_LOG.md and ITERATION_REVIEW.md when users exist |  |
| Funnel | PENDING | FUNNEL_MODEL.md metrics, MVP measurement contract, or not-applicable note |  |
| Launch Maturity | PENDING | LAUNCH_MATURITY_GATE.md when launch-stage ops maturity is in scope |  |
| Scale Moat | PENDING | SCALE_MOAT_REGISTER.md when scale, enterprise, or defensibility is in scope |  |
| Architecture | PENDING | PRODUCT_BLUEPRINT.md, PROJECT_ARCHITECTURE.md, BUILD_PLAN.md |  |
| Tests | PENDING | TEST_PLAN.md and test command output |  |
| Review | PENDING | `/review` result |  |
| TDD Red | PENDING | failing test command and expected failure |  |
| TDD Green | PENDING | passing test command after minimal implementation |  |
| TDD Refactor | PENDING | post-refactor passing command or not-applicable note |  |
| Root Cause | PENDING | `ROOT_CAUSE.md` for bugfixes |  |
| Spec Compliance Review | PENDING | unit output checked against manifest/spec |  |
| Code Quality Review | PENDING | maintainability, simplicity, integration checks |  |
| Unit Context Manifest | PENDING | `.pfo/UNIT_CONTEXT_MANIFEST.json` |  |
| Execution Policy | PENDING | `.pfo/EXECUTION_POLICY.json` |  |
| Permission Matrix | PENDING | `.pfo/PERMISSION_MATRIX.json`, `.pfo/PERMISSION_MATRIX.md` |  |
| Verification Contract | PENDING | `.pfo/VERIFICATION_CONTRACT.json` |  |
| Tool Capability Registry | PENDING | `.pfo/TOOL_CAPABILITY_REGISTRY.json` |  |
| Next Step Approval | PENDING | `NEXT_STEP.md` user decision before the next major implementation step |  |
| Handoff | PENDING | `HANDOFF.md` before session transfer, role switch, delegation, AFK, compaction, or recovery |  |
| Work Verification | PENDING | `pfo verify-work` evidence |  |
| Experiment Loop | PENDING | `.pfo/EXPERIMENT_PROGRAM.md`, `.pfo/EXPERIMENTS.tsv`, fixed metric and keep/discard/crash decision |  |
| Browser Smoke | PENDING | `/browser-check` target, engine, flow, screenshot/log evidence for browser-facing products |  |
| Security | PENDING | `/security-audit` or accepted not-applicable note |  |
| Dependencies | PENDING | `/deps-audit` or accepted not-applicable note |  |
| Hardening | PENDING | `/harden` or accepted non-production note |  |
| Scope Lock | PENDING | `.pfo/SCOPE_LOCK.md`, diff review |  |
| Data Authenticity | PENDING | `.pfo/DATA_POLICY.md`, data-source evidence |  |
| Golden Flows | PENDING | `.pfo/GOLDEN_FLOWS.md`, tests/manual verification |  |
| Regression Contract | PENDING | `.pfo/PROJECT_CONTRACT.md`, behavior checks |  |
| Fallback Policy | PENDING | `.pfo/FALLBACK_POLICY.md`, degraded-mode checks |  |
| Diff Risk | PENDING | `PFO_CONTRACT_GATE.json` when generated |  |
| No Silent Substitution | PENDING | diff scan, project contracts |  |
| Deployment Readiness | PENDING | env vars, build, health check, rollback notes |  |
| Branch Finish | PENDING | PR/merge/keep/discard decision with verification |  |
| Learning Extraction | PENDING | `.codex-memory/LEARNINGS.md` when applicable |  |
| Learning Promotion | PENDING | `.pfo/LEARNING_PROMOTION_GATE.md`, `.codex-memory/LEARNING_PROPOSALS.json` |  |
| Asset Extraction | PENDING | ASSET_REGISTER.md updated after useful repeatable solutions |  |
| Content Pipeline | PENDING | CONTENT_BACKLOG.md updated when learnings can become public content |  |

## Accepted Risks

None yet.

## Next Gate

Run `/review`, `/test`, `/security-audit`, `/deps-audit`, and `/harden` as applicable before deploy readiness.
"""


def generated_phase_context(state: dict, phase: str, note: str) -> str:
    intent = state.get("intent") or "TBD"
    return f"""# Phase Context

Phase: {phase}
Captured: {now_iso()}

## Intent

{intent}

## Decisions

- {note or "TBD: capture implementation decisions before detailed planning."}

## Assumptions

- Defaults are allowed only when they do not change product behavior, data rules, or user-facing flows.
- Any unclear API, UI, data, fallback, or integration behavior must be resolved before execution.

## Open Questions

- TBD

## Planning Impact

- Update `BUILD_PLAN.md`, `EXECUTION_GRAPH.md`, and `.pfo/UNIT_CONTEXT_MANIFEST.json` with decisions from this file.
- Add `.pfo/EXPERIMENT_PROGRAM.md` when the phase uses fixed-budget metric experiments.
- Write `HANDOFF.md` before session transfer, role switch, delegated execution, AFK, compaction, or recovery.
"""


def generated_unit_manifest(project: Path, state: dict, unit_id: str, goal: str, behavior_change: bool = False, bugfix: bool = False) -> dict:
    node = unit_id or state.get("currentNode") or "N1"
    existing = state.get("existingProject", {})
    existing_route = existing.get("currentTaskRoute", "") if isinstance(existing, dict) else ""
    route = " ".join(
        [
            str(state.get("currentTaskRoute", "")),
            str(existing_route),
            goal,
        ]
    ).lower()
    inferred_bugfix = bugfix or "/bugfix" in route or "bugfix" in route
    inferred_behavior_change = behavior_change or inferred_bugfix or "/kickstart" in route
    return {
        "version": 1,
        "unitId": node,
        "goal": goal or f"Execute Product Factory OS unit {node}.",
        "createdAt": now_iso(),
        "requiredInputs": [
            "CODEX.md",
            ".codex-memory/STATE.json",
            ".pfo/PROJECT_CONTRACT.md",
            ".pfo/SCOPE_LOCK.md",
            ".pfo/EXECUTION_POLICY.json",
            ".pfo/PERMISSION_MATRIX.md",
            ".pfo/PERMISSION_MATRIX.json",
            ".pfo/VERIFICATION_CONTRACT.json",
            ".pfo/TOOL_CAPABILITY_REGISTRY.json",
            "IDEA_SCORECARD.md",
            "VALIDATION_PLAN.md",
            "PRODUCT_BLUEPRINT.md",
            "BUILD_PLAN.md",
            "EXECUTION_GRAPH.md",
            "active PIV plan under plans/ before implementation",
            "active implementation report under reports/ before review",
            "NEXT_STEP.md with approved or changed user-facing next step",
            "FEEDBACK_LOG.md and FUNNEL_MODEL.md when user acquisition or iteration is in scope",
            "PHASE_CONTEXT.md when present",
            ".pfo/EXPERIMENT_PROGRAM.md when autonomous measurement-driven iteration is in scope",
            ".pfo/EXPERIMENTS.tsv when autonomous measurement-driven iteration is in scope",
            "HANDOFF.md when switching sessions, roles, delegated agents, AFK execution, compaction, or recovery",
            "ROOT_CAUSE.md for bugfix units",
        ],
        "allowedWriteAreas": [
            "files listed by the active execution graph node",
            "tests for changed behavior",
            "PFO_REPORT.md",
            "plans/",
            "reports/",
            ".codex-memory/STATE.json",
            ".codex-memory/MEMORY.md",
            ".codex-memory/events.jsonl",
        ],
        "forbiddenChanges": [
            "scope outside `.pfo/SCOPE_LOCK.md`",
            "silent production data substitution",
            "unapproved deployment, migration, DNS, or production mutation",
            "golden-flow behavior changes without verification evidence",
            "commands or writes outside `.pfo/EXECUTION_POLICY.json` and `.pfo/PERMISSION_MATRIX.md`",
        ],
        "dependencies": [],
        "verificationCommands": [
            "commands declared in `.pfo/VERIFICATION_CONTRACT.json`",
            "failing test command before implementation for behavior changes",
            "passing test command after minimal implementation",
            "project test command from TEST_PLAN.md",
            "python3 scripts/pfo_contract_gate.py <project> when running from PFO root",
        ],
        "gates": [
            "tddRed",
            "tddGreen",
            "rootCause",
            "specComplianceReview",
            "codeQualityReview",
            "handoff",
            "scopeLock",
            "dataAuthenticity",
            "goldenFlows",
            "regressionContract",
            "fallbackPolicy",
            "diffRisk",
            "noSilentSubstitution",
            "ideaGate",
            "marketValidation",
            "feedbackLoop",
            "funnel",
            "experimentSetup",
            "experimentMetric",
            "experimentDecision",
            "executionPolicy",
            "permissionMatrix",
            "verificationContract",
            "learningPromotion",
            "toolCapabilityRegistry",
            "nextStepApproval",
        ],
        "pivLoop": {
            "sourcePattern": "harness-engineering-demo PIV loop",
            "planPath": piv_paths(node)[0],
            "implementationReportPath": piv_paths(node)[1],
            "sequence": ["plan", "implement", "validate", "review"],
            "rules": [
                "write the PIV plan before implementation",
                "run task-level validation before moving to the next task",
                "run the full verification contract before completion",
                "write the implementation report before review",
            ],
        },
        "engineeringDiscipline": {
            "behaviorChange": inferred_behavior_change,
            "bugfix": inferred_bugfix,
            "strictPlan": True,
            "requiresTdd": "behavior changes",
            "requiresRootCause": "bugfix units",
            "experimentLoop": "fixed budget, protected evaluation, metric-first keep/discard",
            "reviewOrder": ["specCompliance", "codeQuality"],
            "branchFinish": "PR, merge, keep, or discard with fresh verification",
        },
        "experimentLoop": {
            "requiredWhen": "autonomous measurement-driven iteration is in scope",
            "programPath": ".pfo/EXPERIMENT_PROGRAM.md",
            "resultsPath": ".pfo/EXPERIMENTS.tsv",
            "rules": [
                "record a baseline first",
                "keep evaluation harness and protected files immutable",
                "run each attempt under the fixed budget",
                "append metric evidence before keep/discard/crash",
                "prefer simpler code when metric impact is equal",
            ],
        },
        "review": {
            "specCompliance": "Check output against the unit goal, spec, and allowed scope first.",
            "codeQuality": "Check simplicity, maintainability, tests, and integration second.",
        },
        "recovery": "If verification is missing or ambiguous, mark RECOVERY_REQUIRED and create PFO_RECOVERY.md.",
        "project": str(project),
    }


def generated_verification_contract(project: Path, manifest: dict) -> dict:
    unit_id = manifest.get("unitId", "")
    return {
        "version": 1,
        "purpose": "Executable verification contract for the active PFO unit.",
        "unitId": unit_id,
        "createdAt": now_iso(),
        "commands": [
            {
                "id": "pfo-contract-gate",
                "command": f"{sys.executable} {ROOT / 'scripts' / 'pfo_contract_gate.py'} {project}",
                "timeoutSeconds": 90,
                "expectedOutput": "PFO contract gate reports PASS or PASS_WITH_WARNINGS; BLOCKED requires recovery.",
                "passFailParser": "exit_code_zero",
                "required": True,
            }
        ],
        "requiredArtifacts": [
            ".codex-memory/STATE.json",
            ".pfo/UNIT_CONTEXT_MANIFEST.json",
            ".pfo/EXECUTION_POLICY.json",
            ".pfo/PERMISSION_MATRIX.md",
            ".pfo/PERMISSION_MATRIX.json",
            ".pfo/TOOL_CAPABILITY_REGISTRY.json",
            piv_paths(unit_id)[0],
        ],
        "passCriteria": [
            "All required commands exit 0.",
            "Expected output rules match.",
            "Required artifacts exist.",
            "Failures are recorded as recovery, not success.",
        ],
        "failureMode": "RECOVERY_REQUIRED",
    }


def verification_contract_ready(project: Path) -> bool:
    path = project / ".pfo" / "VERIFICATION_CONTRACT.json"
    if not path.is_file():
        return False
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    commands = contract.get("commands", [])
    if not isinstance(commands, list) or not commands:
        return False
    for item in commands:
        if not isinstance(item, dict):
            return False
        for field in ["id", "command", "timeoutSeconds", "expectedOutput", "passFailParser"]:
            if not item.get(field):
                return False
    return True


def slugify_unit(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(value or "unit").strip()).strip("-._").lower()
    return slug or "unit"


def piv_paths(unit_id: str) -> tuple[str, str]:
    slug = slugify_unit(unit_id)
    return f"plans/{slug}-piv-plan.md", f"reports/{slug}-implementation-report.md"


def generated_piv_plan(project: Path, manifest: dict, verification_contract: dict) -> str:
    _, report_path = piv_paths(str(manifest.get("unitId", "")))
    commands = verification_contract.get("commands", [])
    command_lines = []
    for item in commands if isinstance(commands, list) else []:
        if isinstance(item, dict) and item.get("command"):
            command_lines.append(str(item["command"]))
    return f"""# PIV Plan: {manifest.get("unitId", "")}

Project: `{project.name}`
Created: {now_iso()}
Implementation report: `{report_path}`

## Goal

{manifest.get("goal", "Execute the active PFO unit.")}

## Read Before Implementing

{markdown_list(manifest.get("requiredInputs", []), "CODEX.md, BUILD_PLAN.md, EXECUTION_GRAPH.md, and .pfo/UNIT_CONTEXT_MANIFEST.json")}

## Scope

Allowed writes:

{markdown_list(manifest.get("allowedWriteAreas", []), "Only files listed by the active execution graph node")}

Forbidden changes:

{markdown_list(manifest.get("forbiddenChanges", []), "Out-of-scope behavior, real secrets, destructive operations, and production mutations")}

## Ordered Tasks

### Task 1 - Context lock

- What: read the required inputs and identify exact files before editing.
- Validate: active `.pfo/UNIT_CONTEXT_MANIFEST.json` and `.pfo/VERIFICATION_CONTRACT.json` exist.

### Task 2 - Implement the smallest unit

- What: change only the scoped files needed for the unit goal.
- Pattern: follow the closest existing implementation in the target project.
- Gotcha: behavior changes need red and green evidence; bugfixes need `ROOT_CAUSE.md`.
- Validate: run the narrowest relevant command before continuing.

### Task 3 - Full validation gate

- What: run every command declared in `.pfo/VERIFICATION_CONTRACT.json`.
- Validate:

```bash
{chr(10).join(command_lines) if command_lines else "# Add project-specific commands to .pfo/VERIFICATION_CONTRACT.json"}
```

### Task 4 - Report and review

- What: record implementation evidence in `{report_path}`.
- Validate: run spec compliance review before code quality review.

## Acceptance Criteria

- [ ] Unit goal is satisfied.
- [ ] Required commands pass or recovery is recorded.
- [ ] `pfo verify-work {project} --evidence "<commands passed>" --pass-gate` writes `{report_path}`.
- [ ] Spec compliance review is recorded before code quality review.
"""


def generated_piv_report(project: Path, state: dict, evidence: str) -> str:
    current_unit = state.get("currentUnit", {}) if isinstance(state.get("currentUnit"), dict) else {}
    manifest = state.get("unitContextManifest", {}) if isinstance(state.get("unitContextManifest"), dict) else {}
    unit_id = current_unit.get("id") or manifest.get("unitId") or state.get("currentNode") or "unit"
    plan_path, _ = piv_paths(str(unit_id))
    gates = state.get("gateResults", {}) if isinstance(state.get("gateResults"), dict) else {}
    gate_rows = "\n".join(
        f"| {name} | {status or 'PENDING'} |"
        for name, status in sorted(gates.items())
    ) or "| none | PENDING |"
    history = state.get("verificationHistory", []) if isinstance(state.get("verificationHistory"), list) else []
    last_history = history[-5:]
    history_rows = "\n".join(
        f"| {item.get('mode', '') if isinstance(item, dict) else ''} | {item.get('node', '') if isinstance(item, dict) else ''} | {item.get('evidence', '') if isinstance(item, dict) else ''} |"
        for item in last_history
    ) or "| verify-work | | no evidence recorded |"
    return f"""# Implementation Report: {unit_id}

Project: `{project.name}`
Created: {now_iso()}
Plan: `{plan_path}`

## Goal

{current_unit.get("goal") or manifest.get("goal") or "Execute the active PFO unit."}

## Evidence

{evidence or "No evidence string was provided."}

## Validation History

| Mode | Node | Evidence |
|---|---|---|
{history_rows}

## Gate Results

| Gate | Status |
|---|---|
{gate_rows}

## Review Order

- [ ] Spec compliance review recorded with `pfo review-stage --stage spec`.
- [ ] Code quality review recorded with `pfo review-stage --stage quality`.

## Status

Ready for review if all required commands passed and no blocking gate remains.
"""


def clean_tsv_cell(value: object) -> str:
    return str(value if value is not None else "").replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()


def write_tsv_row(path: Path, values: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write("\t".join(clean_tsv_cell(value) for value in values) + "\n")


def resolve_project_file(project: Path, rel_path: str) -> tuple[Path, str]:
    rel = (rel_path or "").strip() or ".pfo/EXPERIMENTS.tsv"
    candidate = Path(rel)
    if candidate.is_absolute():
        raise SystemExit("ERROR: experiment files must be relative to the project")
    resolved_project = project.resolve()
    resolved = (resolved_project / candidate).resolve()
    try:
        normalized = resolved.relative_to(resolved_project).as_posix()
    except ValueError as exc:
        raise SystemExit("ERROR: experiment file escapes the project") from exc
    return resolved, normalized


def metric_improved(direction: str, value: float, best: object) -> bool:
    if best is None:
        return True
    try:
        best_value = float(best)
    except (TypeError, ValueError):
        return True
    if direction == "higher":
        return value > best_value
    return value < best_value


def generated_experiment_program(
    project: Path,
    tag: str,
    metric: str,
    direction: str,
    budget_seconds: int,
    run_command: str,
    baseline_command: str,
    allowed_write_areas: list[str],
    protected_files: list[str],
    results_path: str,
) -> str:
    return f"""# Experiment Program

Project: `{project.name}`
Tag: `{tag}`

## Goal

Run a measurement-first improvement loop with a fixed budget, one primary metric, and explicit keep/discard decisions.

## Metric Contract

- Primary metric: `{metric}`
- Direction: `{direction}`
- Fixed run budget: `{budget_seconds}` seconds
- Baseline command: `{baseline_command or run_command or 'TBD'}`
- Experiment command: `{run_command or 'TBD'}`
- Results log: `{results_path}`

## Scope Contract

Allowed write areas:
{markdown_list(allowed_write_areas, "files listed by the active `.pfo/UNIT_CONTEXT_MANIFEST.json`")}

Protected files and behavior:
{markdown_list(protected_files, "evaluation harness, production data, `.pfo/` contracts, and golden flows")}

## Loop

1. Record a baseline before changing implementation.
2. Change the smallest in-scope surface that could improve the metric.
3. Run the command under the fixed budget.
4. Record metric, runtime, memory if available, complexity cost, and status in `{results_path}`.
5. Keep only if the metric improves, or if the metric is equal and the implementation is simpler.
6. Discard regressions and crashes unless the crash is a trivial fix within the same idea.
7. Promote durable lessons through `pfo learnings` and `pfo improve --from-learnings --propose`.

## Guardrails

- Do not change protected files to improve the metric.
- Do not add dependencies unless the active project plan explicitly allows it.
- Do not treat missing or ambiguous metric output as success.
- Do not perform production, migration, DNS, billing, or external writes without explicit approval.
- Keep branch/worktree cleanup explicit through `pfo finish-branch` when branch state is in scope.
"""


def markdown_list(values: list, fallback: str) -> str:
    items = [str(value).strip() for value in values if str(value).strip()]
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def yaml_quote(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def callout(kind: str, title: str, body: str) -> str:
    lines = str(body or "TBD").splitlines() or ["TBD"]
    quoted = "\n".join(f"> {line}" if line else ">" for line in lines)
    return f"> [!{kind}] {title}\n{quoted}\n"


def callout_list(kind: str, title: str, values: list, fallback: str) -> str:
    items = [str(value).strip() for value in values if str(value).strip()]
    body = "\n".join(f"- {item}" for item in items) if items else fallback
    return callout(kind, title, body)


def graph_roadmap(project: Path, state: dict) -> list[dict[str, str]]:
    graph = project / "EXECUTION_GRAPH.md"
    completed = set(state.get("completedModules", []))
    current = str(state.get("currentNode", ""))
    roadmap: list[dict[str, str]] = []
    if graph.is_file():
        for line in graph.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| N"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) < 2 or not cells[0].startswith("N") or not cells[0][1:].isdigit():
                continue
            step = cells[0]
            if step in completed:
                status = "done"
            elif step == current:
                status = "current"
            else:
                status = "pending"
            roadmap.append({"step": step, "outcome": cells[1], "status": status})
    return roadmap[:12]


def format_roadmap_table(roadmap: list[dict[str, str]]) -> str:
    if not roadmap:
        return "| Step | Outcome | Status |\n|---|---|---|\n| 1 | Define the first product milestone | pending |"
    lines = ["| Step | Outcome | Status |", "|---|---|---|"]
    for item in roadmap:
        lines.append(f"| {item.get('step', '')} | {item.get('outcome', '')} | {item.get('status', '')} |")
    return "\n".join(lines)


def generated_next_step_doc(project: Path, state: dict) -> str:
    steering = ensure_human_steering(state)
    roadmap = steering.get("visibleRoadmap") or graph_roadmap(project, state)
    alternatives = steering.get("alternatives") or [
        "Continue with the recommended step.",
        "Change scope before implementation.",
        "Stop and review the current plan.",
    ]
    questions = steering.get("pendingQuestions") or ["Confirm, change, or stop before the next major implementation step."]
    return f"""# Next Step

This is the user-facing project steering checkpoint. It intentionally avoids internal state-machine terminology.

## Where We Are

- Product: {state.get("intent", "") or project.name}
- Current outcome: {steering.get("lastIterationSummary") or "Planning is ready for user review."}
- Recommended next step: {steering.get("recommendedNextStep") or state.get("nextAction", "") or "Choose the next product step."}
- Approval status: {steering.get("approvalStatus") or "PENDING"}

## Visible Roadmap

{format_roadmap_table(roadmap)}

## Recommended Next Step

- Step: {steering.get("recommendedNextStep") or "Select the first implementation slice."}
- Why now: It is the smallest coherent step that moves the product forward.
- Files likely touched: use `BUILD_PLAN.md` and `.pfo/UNIT_CONTEXT_MANIFEST.json`.
- Verification: use `TEST_PLAN.md` and `.pfo/VERIFICATION_CONTRACT.json`.

## Alternatives

{markdown_list(alternatives, "Continue, change scope, or stop for review.")}

## Decision Needed

{markdown_list(questions, "Confirm the next step before another major implementation iteration starts.")}
"""


def set_next_step_pending(
    project: Path,
    state: dict,
    summary: str,
    recommended: str,
    alternatives: list[str] | None = None,
    questions: list[str] | None = None,
) -> None:
    steering = ensure_human_steering(state)
    steering["approvalRequired"] = True
    steering["approvalStatus"] = "PENDING"
    steering["approvedBy"] = ""
    steering["approvedAt"] = ""
    steering["lastIterationSummary"] = summary
    steering["recommendedNextStep"] = recommended
    steering["alternatives"] = alternatives or [
        "Proceed with the recommended next step.",
        "Revise product scope or priorities first.",
        "Pause implementation and review the plan.",
    ]
    steering["pendingQuestions"] = questions or [
        "Do you approve the recommended next step?",
        "Should scope or priority change before implementation?",
    ]
    steering["visibleRoadmap"] = graph_roadmap(project, state)
    steering["lastPrompt"] = "Ask the user to confirm, change, or stop before continuing."
    state["gateResults"]["nextStepApproval"] = "PENDING"
    state["nextAction"] = f"Ask the user to approve or change the next step: {recommended}"
    add_artifact(state, "NEXT_STEP.md")
    (project / "NEXT_STEP.md").write_text(generated_next_step_doc(project, state), encoding="utf-8")


def generated_handoff_doc(project: Path, state: dict, from_role: str, to_role: str, reason: str, note: str) -> str:
    manifest = state.get("unitContextManifest", {}) if isinstance(state.get("unitContextManifest"), dict) else {}
    current_unit = state.get("currentUnit", {}) if isinstance(state.get("currentUnit"), dict) else {}
    decisions = []
    for item in state.get("decisionLog", [])[-8:]:
        if isinstance(item, dict):
            parts = [str(item.get("event", "")).strip()]
            for key in ["phase", "mode", "status", "note"]:
                value = str(item.get(key, "")).strip()
                if value:
                    parts.append(f"{key}: {value}")
            decisions.append(" | ".join(part for part in parts if part))
        else:
            decisions.append(str(item))
    required_inputs = [
        "CODEX.md",
        ".codex-memory/STATE.json",
        ".pfo/PROJECT_CONTRACT.md",
        ".pfo/SCOPE_LOCK.md",
        "BUILD_PLAN.md",
        "EXECUTION_GRAPH.md",
        "PHASE_CONTEXT.md when present",
        ".pfo/UNIT_CONTEXT_MANIFEST.json when present",
    ]
    required_inputs.extend(manifest.get("requiredInputs", []) if isinstance(manifest.get("requiredInputs"), list) else [])
    verification = manifest.get("verificationCommands", []) if isinstance(manifest.get("verificationCommands"), list) else []
    allowed = manifest.get("allowedWriteAreas", []) if isinstance(manifest.get("allowedWriteAreas"), list) else []
    forbidden = manifest.get("forbiddenChanges", []) if isinstance(manifest.get("forbiddenChanges"), list) else []
    blockers = state.get("blockers", []) if isinstance(state.get("blockers"), list) else []
    goal = current_unit.get("goal") or manifest.get("goal") or state.get("intent") or "Continue the active Product Factory OS task."
    next_action = note or state.get("nextAction") or "Read this handoff, then continue from the active PFO state."
    created = now_iso()
    return f"""---
title: "Handoff"
project: {yaml_quote(project.name)}
stage: {yaml_quote(state.get("currentStage", ""))}
node: {yaml_quote(state.get("currentNode", ""))}
from_role: {yaml_quote(from_role or "current-session")}
to_role: {yaml_quote(to_role or "next-session")}
reason: {yaml_quote(reason or "session-transfer")}
created: {yaml_quote(created)}
tags:
  - pfo/handoff
  - pfo/memory
---

# Handoff

Created: {created}
From: {from_role or "current-session"}
To: {to_role or "next-session"}
Reason: {reason or "session-transfer"}

{callout("todo", "First Action", next_action)}

## Current State

- Project: `{project}`
- Stage: `{state.get("currentStage", "")}`
- Node: `{state.get("currentNode", "")}`
- Unit: `{current_unit.get("id", "")}`
- Next action: {state.get("nextAction", "") or "TBD"}

## Goal

{goal}

## Decisions

{markdown_list(decisions, "No durable decisions recorded yet.")}

## Scope

### Allowed Write Areas

{markdown_list(allowed, "Use the active execution graph node and .pfo/SCOPE_LOCK.md.")}

### Forbidden Changes

{markdown_list(forbidden, "Do not change production data, deployment, migrations, DNS, or out-of-scope files without approval.")}

## Required Inputs

{markdown_list(sorted(set(required_inputs)), "Read CODEX.md and .codex-memory/STATE.json first.")}

## Verification

{markdown_list(verification, "Use TEST_PLAN.md, QUALITY_GATES.md, and the smallest project verification command.")}

## Risks And Blockers

{callout_list("warning", "Risks And Blockers", blockers, "No blockers recorded.")}

## First Action

{next_action}
"""


def generated_recovery_doc(state: dict, reason: str) -> str:
    return f"""# PFO Recovery

Created: {now_iso()}

## Reason

{reason or "Verification evidence is missing or ambiguous."}

## Current State

- Stage: `{state.get("currentStage", "")}`
- Node: `{state.get("currentNode", "")}`
- Unit: `{state.get("currentUnit", {}).get("id", "")}`

## Repair Plan

1. Re-read required inputs from `.pfo/UNIT_CONTEXT_MANIFEST.json`.
2. Identify the smallest failing gate or missing artifact.
3. If this is a bugfix, write or update `ROOT_CAUSE.md` before changing code.
4. Repair only the affected files.
5. Re-run the declared red/green/refactor and verification commands.
6. Run spec compliance review, then code quality review.
7. Update `.codex-memory/STATE.json` and `PFO_REPORT.md`.
"""


def generated_root_cause_doc(summary: str, evidence: str, hypothesis: str) -> str:
    return f"""# Root Cause

Recorded: {now_iso()}

## Summary

{summary or "TBD"}

## Evidence

{evidence or "TBD"}

## Fix Hypothesis

{hypothesis or "TBD"}

## Constraints

- Fix the root cause, not the symptom.
- Change one variable at a time.
- Add or update a regression test before implementation when feasible.
- If three fix attempts fail, stop and question the architecture before continuing.
"""


def generated_brief_html(project: Path, state: dict, mode: str) -> str:
    gates = state.get("gateResults", {})
    steering = state.get("humanSteering", {}) if isinstance(state.get("humanSteering", {}), dict) else {}
    gate_rows = "\n".join(
        f"<tr><td>{escape(str(name))}</td><td>{escape(str(status))}</td></tr>"
        for name, status in gates.items()
    )
    blockers = state.get("blockers", [])
    blocker_items = "\n".join(f"<li>{escape(str(item))}</li>" for item in blockers) or "<li>none</li>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PFO Brief - {escape(project.name)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #171717; background: #f7f7f4; }}
    main {{ max-width: 980px; margin: 0 auto; }}
    h1 {{ font-size: 32px; margin-bottom: 4px; }}
    h2 {{ margin-top: 28px; font-size: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
    .card {{ background: #fff; border: 1px solid #d8d8d0; border-radius: 8px; padding: 14px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    th, td {{ border: 1px solid #d8d8d0; padding: 8px; text-align: left; }}
    th {{ background: #eeeeE8; }}
    code {{ background: #eeeeE8; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
<main>
  <h1>Product Factory OS Brief</h1>
  <p>{escape(mode)} brief for <code>{escape(project.name)}</code>, generated {escape(now_iso())}.</p>
  <section class="grid">
    <div class="card"><strong>Stage</strong><br>{escape(str(state.get("currentStage", "")))}</div>
    <div class="card"><strong>Node</strong><br>{escape(str(state.get("currentNode", "")))}</div>
    <div class="card"><strong>Next</strong><br>{escape(str(state.get("nextAction", "")))}</div>
    <div class="card"><strong>User Approval</strong><br>{escape(str(steering.get("approvalStatus", "")))}</div>
    <div class="card"><strong>Last Good</strong><br>{escape(str(state.get("lastSuccessfulState", "")))}</div>
  </section>
  <h2>Recommended Next Step</h2>
  <p>{escape(str(steering.get("recommendedNextStep", "")))}</p>
  <h2>Gates</h2>
  <table><thead><tr><th>Gate</th><th>Status</th></tr></thead><tbody>{gate_rows}</tbody></table>
  <h2>Blockers</h2>
  <ul>{blocker_items}</ul>
  <h2>Dispatch Journal</h2>
  <pre>{escape(json.dumps(state.get("dispatchJournal", [])[-10:], indent=2, ensure_ascii=False))}</pre>
</main>
</body>
</html>
"""


def cmd_new(args: argparse.Namespace) -> int:
    argv = [args.name, "--idea", args.idea, "--workspace", str(args.workspace)]
    if args.no_plan:
        argv.append("--no-plan")
    return run_script("pfo_new_project.py", argv)


def cmd_adopt(args: argparse.Namespace) -> int:
    argv = ["--write"]
    if args.project:
        argv.extend(["--project", str(args.project)])
    else:
        argv.extend(["--workspace", str(args.workspace)])
    if args.json:
        argv.append("--json")
    should_analyze = args.analyze or args.run_gates or (not args.no_analyze and not args.json)
    if should_analyze:
        argv.append("--analyze")
        if not args.no_report:
            argv.append("--report")
    if args.run_gates:
        argv.append("--run-gates")
    return run_script("adoption_check.py", argv)


def cmd_analyze(args: argparse.Namespace) -> int:
    argv = [str(args.project)]
    if args.run_gates:
        argv.append("--run-gates")
    if args.json:
        argv.append("--json")
    argv.extend(["--timeout", str(args.timeout)])
    code = run_script("existing_project_analyzer.py", argv)
    if code == 0 and args.report:
        return run_script("pfo_report.py", [str(args.project)])
    return code


def cmd_status(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    print(json.dumps({
        "project": str(project),
        "currentStage": state.get("currentStage"),
        "currentNode": state.get("currentNode"),
        "currentUnit": state.get("currentUnit", {}),
        "nextAction": state.get("nextAction"),
        "blockers": state.get("blockers", []),
        "gateResults": state.get("gateResults", {}),
        "recoveryState": state.get("recoveryState", {}),
        "handoff": state.get("handoff", {}),
        "humanSteering": state.get("humanSteering", {}),
        "tddEvidence": state.get("tddEvidence", {}),
        "rootCause": state.get("rootCause", {}),
        "reviewStages": state.get("reviewStages", {}),
        "branchFinish": state.get("branchFinish", {}),
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    starter = load_starter(project, state)
    written = []
    for path, text in [
        (project / "IDEA_SCORECARD.md", generated_idea_scorecard(state)),
        (project / "VALIDATION_PLAN.md", generated_validation_plan(state)),
        (project / "FEEDBACK_LOG.md", generated_feedback_log()),
        (project / "ITERATION_REVIEW.md", generated_iteration_review()),
        (project / "FUNNEL_MODEL.md", generated_funnel_model()),
        (project / "ASSET_REGISTER.md", generated_asset_register()),
        (project / "CONTENT_BACKLOG.md", generated_content_backlog()),
        (project / "PRODUCT_BLUEPRINT.md", generated_blueprint(project, state, starter)),
        (project / "PROJECT_ARCHITECTURE.md", generated_architecture(starter)),
        (project / "BUILD_PLAN.md", generated_build_plan(starter)),
        (project / "TEST_PLAN.md", generated_test_plan(starter)),
        (project / "QUALITY_GATES.md", generated_quality_gates()),
    ]:
        if write_if_missing(path, text):
            written.append(path.name)
    graph = project / "EXECUTION_GRAPH.md"
    if not graph.exists():
        code = run_script("generate_execution_graph.py", [str(project)])
        if code != 0:
            return code
        written.append("EXECUTION_GRAPH.md")
    written.extend(write_alias_documents(project))
    state["currentStage"] = "PLAN_READY"
    state["classification"]["productType"] = state["classification"].get("productType") or starter.get("productType", "")
    state["architecture"]["backend"] = state["architecture"].get("backend") or ", ".join(starter.get("stack", []))
    artifacts = set(state.get("artifacts", []))
    artifacts.update([
        "IDEA_SCORECARD.md",
        "VALIDATION_PLAN.md",
        "FEEDBACK_LOG.md",
        "ITERATION_REVIEW.md",
        "FUNNEL_MODEL.md",
        "ASSET_REGISTER.md",
        "CONTENT_BACKLOG.md",
        "PRODUCT_BLUEPRINT.md",
        "PROJECT_ARCHITECTURE.md",
        "BUILD_PLAN.md",
        "EXECUTION_GRAPH.md",
        "NEXT_STEP.md",
        "TEST_PLAN.md",
        "QUALITY_GATES.md",
        "MASTER_CONTEXT.md",
        "ARCHITECTURE.md",
        "TASKS.md",
        "PROGRESS.md",
        "TESTING.md",
    ])
    state["artifacts"] = sorted(artifacts)
    state.setdefault("decisionLog", []).append({"event": "pfo plan requested", "note": args.note})
    set_next_step_pending(
        project,
        state,
        "Planning artifacts are ready. User review is required before implementation.",
        "Resolve open product decisions, review the visible roadmap, then approve the first implementation slice.",
        [
            "Approve the first implementation slice.",
            "Change the roadmap or MVP scope.",
            "Pause and review the planning documents manually.",
        ],
    )
    save_state(project, state)
    print("OK: plan stage recorded")
    if written:
        print("Generated: " + ", ".join(written))
    else:
        print("Generated: none; existing artifacts preserved")
    return 0


def cmd_discuss(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    phase = args.phase or state.get("currentPhase") or "phase-1"
    path = project / "PHASE_CONTEXT.md"
    if write_if_missing(path, generated_phase_context(state, phase, args.note)):
        print("Generated: PHASE_CONTEXT.md")
    else:
        print("Generated: none; existing PHASE_CONTEXT.md preserved")
    state["currentPhase"] = phase
    state["currentStage"] = "PHASE_DISCUSSION"
    state.setdefault("decisionLog", []).append({"event": "phase discussion", "phase": phase, "note": args.note})
    add_artifact(state, "PHASE_CONTEXT.md")
    set_next_step_pending(
        project,
        state,
        "Phase decisions were captured. Open questions must be resolved before detailed execution.",
        "Review PHASE_CONTEXT.md, resolve open questions, then refresh the plan and unit manifest.",
        [
            "Resolve open questions and continue planning.",
            "Change the phase goal.",
            "Stop implementation until the product owner reviews the decisions.",
        ],
    )
    save_state(project, state)
    return 0


def cmd_manifest(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    manifest = generated_unit_manifest(project, state, args.unit, args.goal, args.behavior_change, args.bugfix)
    pfo_dir = project / ".pfo"
    pfo_dir.mkdir(exist_ok=True)
    manifest_path = pfo_dir / "UNIT_CONTEXT_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    verification_contract = generated_verification_contract(project, manifest)
    verification_path = pfo_dir / "VERIFICATION_CONTRACT.json"
    verification_path.write_text(json.dumps(verification_contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    plan_rel = manifest["pivLoop"]["planPath"]
    plan_path = project / plan_rel
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(generated_piv_plan(project, manifest, verification_contract), encoding="utf-8")
    state["currentStage"] = "UNIT_CONTEXT_READY"
    state["currentNode"] = manifest["unitId"]
    state["currentUnit"] = {
        "id": manifest["unitId"],
        "goal": manifest["goal"],
        "status": "READY",
        "owner": "PFO",
        "startedAt": "",
        "completedAt": "",
        "planPath": plan_rel,
    }
    state["unitContextManifest"] = manifest
    state["executionPolicy"] = {"path": ".pfo/EXECUTION_POLICY.json", "status": "READY"}
    state["permissionMatrix"] = {"path": ".pfo/PERMISSION_MATRIX.json", "humanPath": ".pfo/PERMISSION_MATRIX.md", "status": "READY"}
    state["toolCapabilityRegistry"] = {"path": ".pfo/TOOL_CAPABILITY_REGISTRY.json", "status": "READY"}
    state["verificationContract"] = {"path": ".pfo/VERIFICATION_CONTRACT.json", "status": "READY"}
    state["gateResults"]["executionPolicy"] = "PASSED"
    state["gateResults"]["permissionMatrix"] = "PASSED"
    state["gateResults"]["toolCapabilityRegistry"] = "PASSED"
    state["gateResults"]["verificationContract"] = "PASSED"
    add_artifact(state, ".pfo/UNIT_CONTEXT_MANIFEST.json")
    add_artifact(state, ".pfo/VERIFICATION_CONTRACT.json")
    add_artifact(state, plan_rel)
    set_next_step_pending(
        project,
        state,
        f"Unit {manifest['unitId']} is scoped and ready for user approval.",
        f"Execute PIV plan {plan_rel}: {manifest['goal']}",
        [
            f"Approve unit {manifest['unitId']} and start implementation.",
            "Change the unit goal or scope.",
            "Pause and review BUILD_PLAN.md / EXECUTION_GRAPH.md.",
        ],
    )
    append_event(project, state, "state-change", "READY", {"command": "manifest", "unitId": manifest["unitId"]})
    save_state(project, state)
    print(f"OK: wrote .pfo/UNIT_CONTEXT_MANIFEST.json, .pfo/VERIFICATION_CONTRACT.json, and {plan_rel}")
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    path = project / "HANDOFF.md"
    path.write_text(
        generated_handoff_doc(project, state, args.from_role, args.to_role, args.reason, args.note),
        encoding="utf-8",
    )
    state["currentStage"] = "HANDOFF_READY"
    state["handoff"] = {
        "path": "HANDOFF.md",
        "status": "READY",
        "fromRole": args.from_role,
        "toRole": args.to_role,
        "reason": args.reason,
        "createdAt": now_iso(),
        "nextAction": args.note or state.get("nextAction", ""),
    }
    state.setdefault("gateResults", {})["handoff"] = "PASSED"
    state.setdefault("decisionLog", []).append(
        {
            "event": "handoff created",
            "from": args.from_role,
            "to": args.to_role,
            "reason": args.reason,
            "note": args.note,
        }
    )
    add_artifact(state, "HANDOFF.md")
    state["nextAction"] = "Start the next session by reading HANDOFF.md, then .codex-memory/STATE.json."
    append_event(project, state, "state-change", "READY", {"command": "handoff", "reason": args.reason})
    save_state(project, state)
    print("OK: wrote HANDOFF.md")
    return 0


def cmd_approve_next(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    steering = ensure_human_steering(state)
    steering["approvalRequired"] = False
    steering["approvalStatus"] = "APPROVED"
    steering["approvedBy"] = args.by
    steering["approvedAt"] = now_iso()
    if args.note:
        steering["lastPrompt"] = args.note
    state.setdefault("gateResults", {})["nextStepApproval"] = "PASSED"
    recommended = steering.get("recommendedNextStep") or state.get("nextAction", "")
    state.setdefault("decisionLog", []).append(
        {"event": "next step approved", "by": args.by, "note": args.note, "nextStep": recommended}
    )
    state["nextAction"] = f"Execute the approved next step: {recommended}"
    add_artifact(state, "NEXT_STEP.md")
    (project / "NEXT_STEP.md").write_text(generated_next_step_doc(project, state), encoding="utf-8")
    append_event(project, state, "approval", "PASSED", {"command": "approve-next", "by": args.by, "note": args.note})
    save_state(project, state)
    print("OK: next step approved")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    return run_script("pfo_runner.py", [str(args.project), "--mode", "build"])


def cmd_test(args: argparse.Namespace) -> int:
    return run_script("pfo_runner.py", [str(args.project), "--mode", "test"])


def cmd_review(args: argparse.Namespace) -> int:
    return run_script("pfo_runner.py", [str(args.project), "--mode", "review"])


def cmd_verify_work(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    state["currentStage"] = "VERIFYING_WORK"
    state.setdefault("verificationHistory", []).append(
        {
            "mode": "verify-work",
            "stage": "VERIFYING_WORK",
            "node": state.get("currentNode", ""),
            "evidence": args.evidence,
            "recordedAt": now_iso(),
        }
    )
    state["telemetry"]["verificationCount"] = int(state["telemetry"].get("verificationCount") or 0) + 1
    if args.pass_gate:
        if not verification_contract_ready(project):
            raise SystemExit("ERROR: cannot pass verification without a ready .pfo/VERIFICATION_CONTRACT.json")
        state["gateResults"]["review"] = "PASSED"
        state["gateResults"]["verificationContract"] = "PASSED"
        state["lastSuccessfulState"] = "VERIFYING_WORK"
        state["nextAction"] = "Run tests and quality gates, then proceed to review or next unit."
        manifest = state.get("unitContextManifest", {}) if isinstance(state.get("unitContextManifest"), dict) else {}
        piv_loop = manifest.get("pivLoop", {}) if isinstance(manifest.get("pivLoop"), dict) else {}
        unit_id = state.get("currentUnit", {}).get("id", "") if isinstance(state.get("currentUnit"), dict) else ""
        report_rel = piv_loop.get("implementationReportPath") or piv_paths(unit_id or state.get("currentNode", ""))[1]
        report_path = project / report_rel
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(generated_piv_report(project, state, args.evidence), encoding="utf-8")
        state["lastImplementationReport"] = report_rel
        add_artifact(state, report_rel)
        print(f"Generated: {report_rel}")
    else:
        state["currentStage"] = "RECOVERY_REQUIRED"
        state["recoveryState"] = {
            "status": "REQUIRED",
            "reason": args.evidence or "Verification evidence missing or ambiguous.",
            "retryCount": int(state.get("recoveryState", {}).get("retryCount") or 0),
            "nextRepairAction": "Create or execute the smallest repair plan, then rerun verify-work.",
        }
        (project / "PFO_RECOVERY.md").write_text(generated_recovery_doc(state, args.evidence), encoding="utf-8")
        add_artifact(state, "PFO_RECOVERY.md")
        state["nextAction"] = "Repair the failed or unclear verification path from PFO_RECOVERY.md."
        print("Generated: PFO_RECOVERY.md")
    append_event(
        project,
        state,
        "verification",
        "PASSED" if args.pass_gate else "RECOVERY_REQUIRED",
        {"evidence": args.evidence, "node": state.get("currentNode", "")},
    )
    save_state(project, state)
    print(f"OK: verification recorded as {state['currentStage']}")
    return 0


def cmd_tdd_evidence(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    state["currentStage"] = "TDD_EVIDENCE"
    evidence = state["tddEvidence"]
    if args.red:
        evidence["red"] = args.red
        state["gateResults"]["tddRed"] = "PASSED"
    if args.green:
        evidence["green"] = args.green
        state["gateResults"]["tddGreen"] = "PASSED"
    if args.refactor:
        evidence["refactor"] = args.refactor
        state["gateResults"]["tddRefactor"] = "PASSED"
    if args.no_refactor:
        evidence["refactor"] = "Not applicable: " + args.no_refactor
        state["gateResults"]["tddRefactor"] = "PASSED"
    evidence["lastRecordedAt"] = now_iso()
    if args.red or args.green or args.refactor or args.no_refactor:
        state.setdefault("verificationHistory", []).append(
            {"mode": "tdd-evidence", "node": state.get("currentNode", ""), "evidence": evidence.copy()}
        )
    for gate, field in [("tddRed", "red"), ("tddGreen", "green")]:
        if not evidence.get(field):
            state["gateResults"][gate] = "BLOCKED"
    add_artifact(state, ".codex-memory/STATE.json")
    state["nextAction"] = "Continue only after TDD red and green evidence is recorded for changed behavior."
    append_event(project, state, "verification", "RECORDED", {"command": "tdd-evidence", "evidence": evidence.copy()})
    save_state(project, state)
    print("OK: TDD evidence recorded")
    return 0


def cmd_root_cause(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    state["currentStage"] = "ROOT_CAUSE_ANALYSIS"
    path = project / "ROOT_CAUSE.md"
    path.write_text(generated_root_cause_doc(args.summary, args.evidence, args.hypothesis), encoding="utf-8")
    state["rootCause"] = {
        "status": "RECORDED" if args.summary and args.evidence else "INCOMPLETE",
        "summary": args.summary,
        "evidence": args.evidence,
        "hypothesis": args.hypothesis,
        "recordedAt": now_iso(),
    }
    state["gateResults"]["rootCause"] = "PASSED" if args.summary and args.evidence else "BLOCKED"
    add_artifact(state, "ROOT_CAUSE.md")
    state["nextAction"] = "Use ROOT_CAUSE.md to implement one focused fix and verify with a regression test."
    append_event(project, state, "gate", state["gateResults"]["rootCause"], {"command": "root-cause", "summary": args.summary})
    save_state(project, state)
    print("OK: wrote ROOT_CAUSE.md")
    return 0


def cmd_review_stage(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    state["currentStage"] = "TWO_STAGE_REVIEW"
    key = "specCompliance" if args.stage == "spec" else "codeQuality"
    gate = "specComplianceReview" if args.stage == "spec" else "codeQualityReview"
    state["reviewStages"][key] = {
        "status": args.status,
        "evidence": args.evidence,
        "recordedAt": now_iso(),
    }
    state["gateResults"][gate] = args.status
    state.setdefault("verificationHistory", []).append(
        {"mode": "review-stage", "stage": args.stage, "status": args.status, "evidence": args.evidence}
    )
    state["nextAction"] = (
        "Run code quality review after spec compliance passes."
        if args.stage == "spec" and args.status == "PASSED"
        else "Resolve review findings or proceed to the next gate."
    )
    append_event(project, state, "gate", args.status, {"command": "review-stage", "stage": args.stage, "evidence": args.evidence})
    save_state(project, state)
    print(f"OK: {args.stage} review recorded as {args.status}")
    return 0


def cmd_finish_branch(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    state["currentStage"] = "BRANCH_FINISH"
    status = "PASSED" if args.verification else "BLOCKED"
    state["branchFinish"] = {
        "status": status,
        "mode": args.mode,
        "verification": args.verification,
        "remoteBranch": args.remote_branch,
        "prUrl": args.pr_url,
        "cleanupDecision": args.cleanup_decision,
        "recordedAt": now_iso(),
    }
    (project / "BRANCH_FINISH.md").write_text(
        "\n".join(
            [
                "# Branch Finish",
                "",
                f"Recorded: {state['branchFinish']['recordedAt']}",
                "",
                "## Decision",
                "",
                f"- Mode: {args.mode}",
                f"- Branch: {args.remote_branch or 'TBD'}",
                f"- PR URL: {args.pr_url or 'TBD'}",
                "",
                "## Verification",
                "",
                args.verification or "TBD",
                "",
                "## Cleanup",
                "",
                args.cleanup_decision or "TBD",
                "",
            ]
        ),
        encoding="utf-8",
    )
    add_artifact(state, "BRANCH_FINISH.md")
    state["gateResults"]["branchFinish"] = status
    if not args.verification:
        state.setdefault("blockers", []).append("Branch finish requires fresh verification evidence.")
    state["nextAction"] = "Finish branch using the recorded PR/merge/keep/discard decision."
    append_event(project, state, "gate", status, {"command": "finish-branch", "mode": args.mode, "verification": args.verification})
    save_state(project, state)
    print(f"OK: branch finish recorded as {status}")
    return 0


def cmd_learnings(args: argparse.Namespace) -> int:
    argv = ["record", str(args.project)]
    for flag in ["scope", "decision", "lesson", "pattern", "surprise", "problem", "rule"]:
        value = getattr(args, flag)
        if value:
            argv.extend([f"--{flag}", value])
    for evidence in args.evidence or []:
        argv.extend(["--evidence", evidence])
    if args.confidence is not None:
        argv.extend(["--confidence", str(args.confidence)])
    return run_script("pfo_learn.py", argv)


def cmd_improve(args: argparse.Namespace) -> int:
    if not args.from_learnings:
        print("ERROR: improve currently requires --from-learnings")
        return 2
    if not args.propose:
        print("ERROR: improve currently requires --propose")
        return 2
    argv = ["propose", str(args.project), "--min-confidence", str(args.min_confidence)]
    if args.registry:
        argv.extend(["--registry", str(args.registry)])
    if args.promotion_target:
        argv.extend(["--promotion-target", args.promotion_target])
    for artifact in args.promotion_artifact or []:
        argv.extend(["--promotion-artifact", artifact])
    for check in args.promotion_check or []:
        argv.extend(["--promotion-check", check])
    if args.review_status:
        argv.extend(["--review-status", args.review_status])
    return run_script("pfo_learn.py", argv)


def cmd_learning_gate(args: argparse.Namespace) -> int:
    argv = ["gate", str(args.project)]
    if args.require_approved:
        argv.append("--require-approved")
    return run_script("pfo_learn.py", argv)


def cmd_permission_check(args: argparse.Namespace) -> int:
    argv = [str(args.project)]
    if args.capability:
        argv.extend(["--capability", args.capability])
    if args.path:
        argv.extend(["--path", args.path])
    if args.command_text:
        argv.extend(["--command", args.command_text])
    if args.approved:
        argv.append("--approved")
    if args.json:
        argv.append("--json")
    return run_script("pfo_permission_gate.py", argv)


def cmd_event(args: argparse.Namespace) -> int:
    if args.event_action == "validate":
        return run_script("pfo_event_log.py", ["validate", str(args.project)])
    argv = [
        "record",
        str(args.project),
        "--event-type",
        args.event_type,
        "--status",
        args.status,
        "--source",
        args.source,
    ]
    for flag, value in [
        ("--event-id", args.event_id),
        ("--command", args.command_text),
        ("--cost-notes", args.cost_notes),
        ("--token-notes", args.token_notes),
        ("--reason", args.reason),
    ]:
        if value:
            argv.extend([flag, str(value)])
    if args.exit_code is not None:
        argv.extend(["--exit-code", str(args.exit_code)])
    if args.duration_seconds is not None:
        argv.extend(["--duration-seconds", str(args.duration_seconds)])
    return run_script("pfo_event_log.py", argv)


def cmd_tool_registry(args: argparse.Namespace) -> int:
    return run_script("validate_tool_registry.py", [str(args.project / ".pfo" / "TOOL_CAPABILITY_REGISTRY.json")])


def cmd_experiment_init(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    tag = args.tag or datetime.now(timezone.utc).strftime("exp-%Y%m%d")
    program_path, program_rel = resolve_project_file(project, args.program_file)
    results_path, results_rel = resolve_project_file(project, args.result_file)
    allowed_write_areas = args.allowed_write or []
    protected_files = args.protected_file or [
        "evaluation harness",
        "production data and provider outputs",
        "project `.pfo/` contracts",
        "golden flows unless verification evidence is explicit",
    ]

    program_path.parent.mkdir(parents=True, exist_ok=True)
    if not program_path.exists():
        program_path.write_text(
            generated_experiment_program(
                project,
                tag,
                args.metric,
                args.direction,
                args.budget_seconds,
                args.run_command,
                args.baseline_command,
                allowed_write_areas,
                protected_files,
                results_rel,
            ),
            encoding="utf-8",
        )
        print(f"Generated: {program_rel}")
    else:
        print(f"Generated: none; existing {program_rel} preserved")

    if not results_path.exists():
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(
            "run_id\tcommit\tmetric\tmetric_value\tbudget_seconds\trun_seconds\tmemory_gb\tstatus\tcomplexity_cost\tdescription\n",
            encoding="utf-8",
        )
        print(f"Generated: {results_rel}")

    state["currentStage"] = "EXPERIMENT_READY"
    state["experimentLoop"] = {
        "status": "READY",
        "tag": tag,
        "programPath": program_rel,
        "resultsPath": results_rel,
        "metric": {"name": args.metric, "direction": args.direction, "bestValue": None, "bestRunId": ""},
        "budgetSeconds": args.budget_seconds,
        "runCommand": args.run_command,
        "baselineCommand": args.baseline_command or args.run_command,
        "allowedWriteAreas": allowed_write_areas,
        "protectedFiles": protected_files,
        "baselineRecorded": False,
        "lastRun": {},
    }
    state["gateResults"]["experimentSetup"] = "PASSED"
    state["nextAction"] = f"Run the baseline command, then record it with `pfo experiment-record {project}`."
    state.setdefault("decisionLog", []).append(
        {
            "event": "experiment loop initialized",
            "tag": tag,
            "metric": args.metric,
            "direction": args.direction,
            "budgetSeconds": args.budget_seconds,
        }
    )
    add_artifact(state, program_rel)
    add_artifact(state, results_rel)
    append_event(project, state, "state-change", "READY", {"command": "experiment-init", "tag": tag, "metric": args.metric})
    save_state(project, state)
    print("OK: experiment loop initialized")
    return 0


def cmd_experiment_record(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    loop = state.get("experimentLoop", {})
    if not isinstance(loop, dict) or not loop.get("resultsPath"):
        print("ERROR: run `pfo experiment-init <project>` first")
        return 2

    metric = loop.get("metric", {}) if isinstance(loop.get("metric"), dict) else {}
    metric_name = args.metric or metric.get("name") or "primary_metric"
    direction = args.direction or metric.get("direction") or "lower"
    metric_value = args.metric_value
    status = args.status
    if status == "auto":
        if metric_value is None:
            status = "crash"
        elif metric_improved(direction, metric_value, metric.get("bestValue")):
            status = "keep"
        else:
            status = "discard"
    if status != "crash" and metric_value is None:
        print("ERROR: --metric-value is required unless status is crash")
        return 2

    run_id = args.run_id or datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")
    results_path, results_rel = resolve_project_file(project, args.result_file or loop.get("resultsPath", ""))
    if not results_path.exists():
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(
            "run_id\tcommit\tmetric\tmetric_value\tbudget_seconds\trun_seconds\tmemory_gb\tstatus\tcomplexity_cost\tdescription\n",
            encoding="utf-8",
        )

    metric_text = f"{metric_value:.6f}" if metric_value is not None else "0.000000"
    memory_text = f"{args.memory_gb:.1f}" if args.memory_gb is not None else "0.0"
    run_seconds_text = f"{args.run_seconds:.1f}" if args.run_seconds is not None else "0.0"
    write_tsv_row(
        results_path,
        [
            run_id,
            args.commit,
            metric_name,
            metric_text,
            loop.get("budgetSeconds") or args.budget_seconds or "",
            run_seconds_text,
            memory_text,
            status,
            args.complexity_cost,
            args.description,
        ],
    )

    best_value = metric.get("bestValue")
    best_run_id = metric.get("bestRunId", "")
    if status == "keep" and metric_value is not None and metric_improved(direction, metric_value, best_value):
        best_value = metric_value
        best_run_id = run_id

    loop["status"] = "EVALUATED"
    loop["resultsPath"] = results_rel
    loop["metric"] = {
        "name": metric_name,
        "direction": direction,
        "bestValue": best_value,
        "bestRunId": best_run_id,
    }
    loop["baselineRecorded"] = bool(loop.get("baselineRecorded")) or status != "crash"
    loop["lastRun"] = {
        "runId": run_id,
        "commit": args.commit,
        "metricValue": metric_value,
        "status": status,
        "complexityCost": args.complexity_cost,
        "description": args.description,
        "recordedAt": now_iso(),
    }
    state["experimentLoop"] = loop
    state["currentStage"] = "EXPERIMENT_EVALUATED"
    state["gateResults"]["experimentMetric"] = "PASSED" if metric_value is not None else "BLOCKED"
    state["gateResults"]["experimentDecision"] = "PASSED_WITH_WARNINGS" if status == "crash" else "PASSED"
    state.setdefault("verificationHistory", []).append(
        {
            "mode": "experiment-record",
            "runId": run_id,
            "metric": metric_name,
            "value": metric_value,
            "status": status,
            "description": args.description,
        }
    )
    state.setdefault("dispatchJournal", []).append(
        {"unit": state.get("currentNode", ""), "mode": "experiment", "runId": run_id, "status": status}
    )
    telemetry = state.setdefault("telemetry", {})
    telemetry["verificationCount"] = int(telemetry.get("verificationCount") or 0) + 1
    telemetry["lastCommand"] = loop.get("runCommand", "")
    telemetry["lastDurationSeconds"] = args.run_seconds
    add_artifact(state, results_rel)
    if status == "keep":
        state["nextAction"] = "Continue from the kept experiment and try the next smallest metric-improving idea."
    elif status == "discard":
        state["nextAction"] = "Discard this experiment's implementation change, keep the TSV evidence, and try a new idea."
    else:
        state["nextAction"] = "Treat the crash as a failed experiment unless the fix is trivial and in scope."
    append_event(project, state, "verification", status.upper(), {"command": "experiment-record", "runId": run_id, "metric": metric_name, "value": metric_value})
    save_state(project, state)
    print(f"OK: recorded experiment {run_id} as {status}")
    return 0


def cmd_brief(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    path = project / "PFO_BRIEF.html"
    path.write_text(generated_brief_html(project, state, args.mode), encoding="utf-8")
    state.setdefault("briefArtifacts", []).append(str(path))
    add_artifact(state, "PFO_BRIEF.html")
    state["nextAction"] = "Review PFO_BRIEF.html for status, gates, blockers, and dispatch history."
    append_event(project, state, "state-change", "RECORDED", {"command": "brief", "mode": args.mode})
    save_state(project, state)
    print(f"OK: wrote {path}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    return run_script("validate_project.py", [str(args.project)])


def cmd_contracts(args: argparse.Namespace) -> int:
    argv = [str(args.project)]
    if args.json:
        argv.append("--json")
    if args.write:
        argv.append("--write")
    if args.strict:
        argv.append("--strict")
    return run_script("pfo_contract_gate.py", argv)


def cmd_resume(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    print("CURRENT STATE:", state.get("currentStage", ""))
    print("CURRENT NODE:", state.get("currentNode", ""))
    print("NEXT ACTION:", state.get("nextAction", ""))
    if (project / "HANDOFF.md").is_file():
        print("HANDOFF:", "HANDOFF.md")
    return 0


def cmd_voice(args: argparse.Namespace) -> int:
    return run_script("voice_intent.py", [args.text, "--workspace", str(args.workspace)])


def cmd_metrics(args: argparse.Namespace) -> int:
    return run_script("pfo_metrics.py", [str(args.workspace)])


def cmd_report(args: argparse.Namespace) -> int:
    return run_script("pfo_report.py", [str(args.project)])


def cmd_export(args: argparse.Namespace) -> int:
    return run_script("export_integrations.py", [str(args.project), "--target", args.target])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pfo", description="Product Factory OS runtime CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="Bootstrap a new PFO project.")
    new.add_argument("name")
    new.add_argument("--idea", default="")
    new.add_argument("--workspace", type=Path, default=WORKSPACE)
    new.add_argument("--no-plan", action="store_true", help="Skip automatic plan/report generation.")
    new.set_defaults(func=cmd_new)

    adopt = sub.add_parser("adopt", help="Adopt existing workspace projects into PFO.")
    adopt.add_argument("project", type=Path, nargs="?")
    adopt.add_argument("--workspace", type=Path, default=WORKSPACE)
    adopt.add_argument("--json", action="store_true")
    adopt.add_argument("--analyze", action="store_true", help="Run analyzer explicitly; full adoption does this by default.")
    adopt.add_argument("--no-analyze", action="store_true", help="Only write missing runtime files.")
    adopt.add_argument("--no-report", action="store_true", help="Do not write PFO_REPORT.md during full adoption.")
    adopt.add_argument("--run-gates", action="store_true", help="Run detected gates during analysis.")
    adopt.set_defaults(func=cmd_adopt)

    analyze = sub.add_parser("analyze", help="Analyze an existing project, detect stack/commands, run gates, and update PFO state.")
    analyze.add_argument("project", type=Path)
    analyze.add_argument("--run-gates", action="store_true")
    analyze.add_argument("--timeout", type=int, default=90)
    analyze.add_argument("--json", action="store_true")
    analyze.add_argument("--report", action="store_true", help="Regenerate PFO_REPORT.md after analysis.")
    analyze.set_defaults(func=cmd_analyze)

    discuss = sub.add_parser("discuss", help="Capture phase decisions before detailed planning.")
    discuss.add_argument("project", type=Path)
    discuss.add_argument("--phase", default="")
    discuss.add_argument("--note", default="")
    discuss.set_defaults(func=cmd_discuss)

    handoff = sub.add_parser("handoff", help="Write a session-to-session handoff artifact.")
    handoff.add_argument("project", type=Path)
    handoff.add_argument("--from-role", default="current-session")
    handoff.add_argument("--to-role", default="next-session")
    handoff.add_argument("--reason", default="session-transfer")
    handoff.add_argument("--note", default="")
    handoff.set_defaults(func=cmd_handoff)

    approve_next = sub.add_parser("approve-next", help="Record user approval for the recommended next implementation step.")
    approve_next.add_argument("project", type=Path)
    approve_next.add_argument("--by", default="user")
    approve_next.add_argument("--note", default="")
    approve_next.set_defaults(func=cmd_approve_next)

    manifest = sub.add_parser("manifest", help="Write a task-scoped unit context manifest.")
    manifest.add_argument("project", type=Path)
    manifest.add_argument("--unit", default="")
    manifest.add_argument("--goal", default="")
    manifest.add_argument("--behavior-change", action="store_true", help="Require TDD evidence for this unit.")
    manifest.add_argument("--bugfix", action="store_true", help="Require ROOT_CAUSE.md before implementation.")
    manifest.set_defaults(func=cmd_manifest)

    for name, func in [
        ("status", cmd_status),
        ("plan", cmd_plan),
        ("build", cmd_build),
        ("test", cmd_test),
        ("review", cmd_review),
        ("validate", cmd_validate),
        ("contracts", cmd_contracts),
        ("resume", cmd_resume),
        ("report", cmd_report),
    ]:
        item = sub.add_parser(name)
        item.add_argument("project", type=Path)
        if name == "plan":
            item.add_argument("--note", default="")
        if name == "contracts":
            item.add_argument("--json", action="store_true")
            item.add_argument("--write", action="store_true")
            item.add_argument("--strict", action="store_true")
        item.set_defaults(func=func)

    verify_work = sub.add_parser("verify-work", help="Record post-unit verification; fail closed by default.")
    verify_work.add_argument("project", type=Path)
    verify_work.add_argument("--evidence", default="")
    verify_work.add_argument("--pass-gate", action="store_true", help="Mark verification as passed when evidence is definitive.")
    verify_work.set_defaults(func=cmd_verify_work)

    tdd = sub.add_parser("tdd-evidence", help="Record red/green/refactor evidence for changed behavior.")
    tdd.add_argument("project", type=Path)
    tdd.add_argument("--red", default="", help="Failing test command and expected failure evidence.")
    tdd.add_argument("--green", default="", help="Passing test command after minimal implementation.")
    tdd.add_argument("--refactor", default="", help="Passing command after refactor.")
    tdd.add_argument("--no-refactor", default="", help="Reason refactor step is not applicable.")
    tdd.set_defaults(func=cmd_tdd_evidence)

    root_cause = sub.add_parser("root-cause", help="Write ROOT_CAUSE.md and record bugfix root-cause evidence.")
    root_cause.add_argument("project", type=Path)
    root_cause.add_argument("--summary", default="")
    root_cause.add_argument("--evidence", default="")
    root_cause.add_argument("--hypothesis", default="")
    root_cause.set_defaults(func=cmd_root_cause)

    review_stage = sub.add_parser("review-stage", help="Record spec-compliance or code-quality review stage.")
    review_stage.add_argument("project", type=Path)
    review_stage.add_argument("--stage", choices=["spec", "quality"], required=True)
    review_stage.add_argument("--status", choices=["BLOCKED", "PASSED_WITH_WARNINGS", "PASSED"], required=True)
    review_stage.add_argument("--evidence", default="")
    review_stage.set_defaults(func=cmd_review_stage)

    finish_branch = sub.add_parser("finish-branch", help="Record PR, merge, keep, or discard branch finish decision.")
    finish_branch.add_argument("project", type=Path)
    finish_branch.add_argument("--mode", choices=["pr", "merge", "keep", "discard"], required=True)
    finish_branch.add_argument("--verification", default="")
    finish_branch.add_argument("--remote-branch", default="")
    finish_branch.add_argument("--pr-url", default="")
    finish_branch.add_argument("--cleanup-decision", default="")
    finish_branch.set_defaults(func=cmd_finish_branch)

    learnings = sub.add_parser("learnings", help="Append durable decisions, lessons, patterns, and surprises.")
    learnings.add_argument("project", type=Path)
    learnings.add_argument("--decision", default="")
    learnings.add_argument("--lesson", default="")
    learnings.add_argument("--pattern", default="")
    learnings.add_argument("--surprise", default="")
    learnings.add_argument("--scope", default="")
    learnings.add_argument("--problem", default="")
    learnings.add_argument("--rule", default="")
    learnings.add_argument("--evidence", action="append", default=[])
    learnings.add_argument("--confidence", type=float, default=None)
    learnings.set_defaults(func=cmd_learnings)

    improve = sub.add_parser("improve", help="Propose PFO runtime improvements from structured learnings.")
    improve.add_argument("project", type=Path)
    improve.add_argument("--from-learnings", action="store_true")
    improve.add_argument("--propose", action="store_true")
    improve.add_argument("--min-confidence", type=float, default=0.0)
    improve.add_argument("--registry", type=Path, default=None)
    improve.add_argument("--promotion-target", choices=["test", "hook", "doc", "rule", "linter", "validator", "template", "skill", "route"], default="")
    improve.add_argument("--promotion-artifact", action="append", default=[])
    improve.add_argument("--promotion-check", action="append", default=[])
    improve.add_argument("--review-status", choices=["PENDING", "APPROVED", "REJECTED"], default="PENDING")
    improve.set_defaults(func=cmd_improve)

    learning_gate = sub.add_parser("learning-gate", help="Validate learning proposals before runtime promotion.")
    learning_gate.add_argument("project", type=Path)
    learning_gate.add_argument("--require-approved", action="store_true")
    learning_gate.set_defaults(func=cmd_learning_gate)

    permission_check = sub.add_parser("permission-check", help="Validate permission matrix or check one capability.")
    permission_check.add_argument("project", type=Path)
    permission_check.add_argument("--capability", choices=["read", "write", "test", "commit", "push", "deploy", "external_api", "secrets"])
    permission_check.add_argument("--path", default="")
    permission_check.add_argument("--command-text", default="")
    permission_check.add_argument("--approved", action="store_true")
    permission_check.add_argument("--json", action="store_true")
    permission_check.set_defaults(func=cmd_permission_check)

    event = sub.add_parser("event", help="Record or validate structured events.")
    event.add_argument("event_action", choices=["record", "validate"])
    event.add_argument("project", type=Path)
    event.add_argument("--event-type", choices=["command", "gate", "approval", "verification", "state-change", "learning", "external-tool", "error"], default="command")
    event.add_argument("--status", default="RECORDED")
    event.add_argument("--source", default="pfo-cli")
    event.add_argument("--event-id", default="")
    event.add_argument("--command-text", default="")
    event.add_argument("--exit-code", type=int, default=None)
    event.add_argument("--duration-seconds", type=float, default=None)
    event.add_argument("--cost-notes", default="")
    event.add_argument("--token-notes", default="")
    event.add_argument("--reason", default="")
    event.set_defaults(func=cmd_event)

    tool_registry = sub.add_parser("tool-registry", help="Validate project tool capability registry.")
    tool_registry.add_argument("project", type=Path)
    tool_registry.set_defaults(func=cmd_tool_registry)

    experiment_init = sub.add_parser("experiment-init", help="Create an Autoresearch-style fixed-budget experiment loop.")
    experiment_init.add_argument("project", type=Path)
    experiment_init.add_argument("--tag", default="")
    experiment_init.add_argument("--metric", default="primary_metric")
    experiment_init.add_argument("--direction", choices=["lower", "higher"], default="lower")
    experiment_init.add_argument("--budget-seconds", type=int, default=300)
    experiment_init.add_argument("--run-command", default="")
    experiment_init.add_argument("--baseline-command", default="")
    experiment_init.add_argument("--allowed-write", action="append", default=[])
    experiment_init.add_argument("--protected-file", action="append", default=[])
    experiment_init.add_argument("--program-file", default=".pfo/EXPERIMENT_PROGRAM.md")
    experiment_init.add_argument("--result-file", default=".pfo/EXPERIMENTS.tsv")
    experiment_init.set_defaults(func=cmd_experiment_init)

    experiment_record = sub.add_parser("experiment-record", help="Append an experiment result and update keep/discard state.")
    experiment_record.add_argument("project", type=Path)
    experiment_record.add_argument("--run-id", default="")
    experiment_record.add_argument("--commit", default="")
    experiment_record.add_argument("--metric", default="")
    experiment_record.add_argument("--metric-value", type=float, default=None)
    experiment_record.add_argument("--direction", choices=["lower", "higher"], default="")
    experiment_record.add_argument("--budget-seconds", type=int, default=None)
    experiment_record.add_argument("--run-seconds", type=float, default=None)
    experiment_record.add_argument("--memory-gb", type=float, default=None)
    experiment_record.add_argument("--status", choices=["auto", "keep", "discard", "crash"], default="auto")
    experiment_record.add_argument("--complexity-cost", type=int, default=0)
    experiment_record.add_argument("--description", default="")
    experiment_record.add_argument("--result-file", default="")
    experiment_record.set_defaults(func=cmd_experiment_record)

    brief = sub.add_parser("brief", help="Generate a self-contained HTML project brief.")
    brief.add_argument("project", type=Path)
    brief.add_argument("--mode", choices=["diagram", "plan", "diff", "recap", "table", "slides"], default="recap")
    brief.set_defaults(func=cmd_brief)

    voice = sub.add_parser("voice", help="Normalize a voice command into PFO intent.")
    voice.add_argument("text")
    voice.add_argument("--workspace", type=Path, default=WORKSPACE)
    voice.set_defaults(func=cmd_voice)

    metrics = sub.add_parser("metrics", help="Collect workspace PFO metrics.")
    metrics.add_argument("--workspace", type=Path, default=WORKSPACE)
    metrics.set_defaults(func=cmd_metrics)

    export = sub.add_parser("export", help="Export project state for external tools.")
    export.add_argument("project", type=Path)
    export.add_argument("--target", choices=["github", "linear", "notion", "google-drive", "obsidian"], required=True)
    export.set_defaults(func=cmd_export)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
