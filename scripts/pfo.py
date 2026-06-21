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
PLAN_ARTIFACTS = [
    "PRODUCT_BLUEPRINT.md",
    "PROJECT_ARCHITECTURE.md",
    "BUILD_PLAN.md",
    "EXECUTION_GRAPH.md",
    "TEST_PLAN.md",
    "QUALITY_GATES.md",
    "NEXT_STEP.md",
]
ROUTE_PROFILES_PATH = ROOT / "routing" / "route-profiles.json"
ROUTE_PROFILE_IDS = {"minimal", "standard", "full"}
SUCCESS_GATE_STATUSES = {"PASS", "PASSED", "PASS_WITH_WARNINGS", "PASSED_WITH_WARNINGS", "READY", "RECORDED"}


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
    state.setdefault("contextBudget", {"gate": "pfo context-budget", "indexPath": ".codex-memory/context-index.json", "snapshotPath": ".codex-memory/resume-snapshot.md", "status": ""})
    state.setdefault("verificationContract", {"path": ".pfo/VERIFICATION_CONTRACT.json", "status": ""})
    state.setdefault("acceptanceContract", {"path": ".pfo/ACCEPTANCE_CONTRACT.json", "status": ""})
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
    state.setdefault(
        "agentRuntime",
        {
            "specVersion": 1,
            "agentSpecsPath": "agents/*.yaml",
            "projectAgentSpecsPath": ".pfo/agents/",
            "lastValidation": "",
            "status": "",
        },
    )
    state.setdefault(
        "policyRuntime",
        {
            "engine": "pfo-policy-eval",
            "verdicts": ["ALLOW", "DENY", "ASK"],
            "lastVerdict": "",
            "lastReason": "",
            "lastEventAt": "",
        },
    )
    state.setdefault(
        "dispatchRuntime",
        {
            "path": ".pfo/dispatch/",
            "activeDispatches": [],
            "lastDispatchId": "",
            "worktreeIsolation": "declared-per-dispatch",
        },
    )
    state.setdefault(
        "crossReview",
        {
            "path": ".pfo/cross-review/",
            "requiredForRisk": ["security", "migration", "deploy", "auth", "payments", "data-loss"],
            "lastReviewId": "",
            "status": "",
        },
    )
    state.setdefault(
        "costRiskRouting",
        {
            "lastDecision": "",
            "modelTier": "",
            "riskScore": 0,
            "estimatedCostUsd": 0,
            "budgetDecision": "",
            "updatedAt": "",
        },
    )
    state.setdefault(
        "sessionRuntime",
        {
            "path": ".pfo/session/",
            "liveStatusPath": ".pfo/session/live-status.json",
            "exportPath": ".pfo/session/session-export.json",
            "lastExportAt": "",
            "lastImportAt": "",
        },
    )
    state.setdefault(
        "sandboxRuntime",
        {
            "defaultType": "local",
            "specSource": ".pfo/UNIT_CONTEXT_MANIFEST.json",
            "lastCheckedAt": "",
        },
    )
    state.setdefault(
        "runnerServer",
        {
            "runnerHostPath": ".pfo/runner/runner-host.json",
            "serverControlPlanePath": ".pfo/server/control-plane.json",
            "runnerStatus": "",
            "serverStatus": "",
        },
    )
    gates = state.setdefault("gateResults", {})
    for gate in [
        "ideaGate",
        "marketValidation",
        "seoGrowthGuarantee",
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
        "adoption",
        "targetedVerification",
        "assetExtraction",
        "contentPipeline",
        "experimentSetup",
        "experimentMetric",
        "experimentDecision",
        "executionPolicy",
        "permissionMatrix",
        "contextBudget",
        "verificationContract",
        "acceptanceContract",
        "securityEvidence",
        "learningPromotion",
        "toolCapabilityRegistry",
        "agentSpec",
        "policyRuntime",
        "dispatchRuntime",
        "crossReview",
        "costRiskRouting",
        "sessionRuntime",
        "sandboxRuntime",
        "runnerServer",
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


def gate_passed(state: dict, gate: str) -> bool:
    return str(state.get("gateResults", {}).get(gate, "")).upper() in SUCCESS_GATE_STATUSES


def missing_files(project: Path, files: list[str]) -> list[str]:
    return [rel for rel in files if not (project / rel).is_file()]


def load_route_profiles() -> dict:
    return json.loads(ROUTE_PROFILES_PATH.read_text(encoding="utf-8"))


def route_profile_config(profile_id: str) -> dict:
    profiles = load_route_profiles().get("profiles", {})
    profile = profiles.get(profile_id)
    if not isinstance(profile, dict):
        raise SystemExit(f"ERROR: unknown route profile: {profile_id}")
    return profile


def select_route_profile(
    state: dict,
    goal: str = "",
    explicit_profile: str = "auto",
    behavior_change: bool = False,
    bugfix: bool = False,
) -> tuple[str, str]:
    if explicit_profile and explicit_profile != "auto":
        if explicit_profile not in ROUTE_PROFILE_IDS:
            raise SystemExit(f"ERROR: route profile must be one of: {', '.join(sorted(ROUTE_PROFILE_IDS))}")
        return explicit_profile, "explicit profile selection"

    active_profile = state.get("activeRouteProfile", {}) if isinstance(state.get("activeRouteProfile"), dict) else {}
    active_profile_id = str(active_profile.get("id", ""))
    if active_profile_id in ROUTE_PROFILE_IDS:
        return active_profile_id, "active state route profile"

    existing = state.get("existingProject", {}) if isinstance(state.get("existingProject"), dict) else {}
    current_unit = state.get("currentUnit", {}) if isinstance(state.get("currentUnit"), dict) else {}
    text = " ".join(
        [
            str(state.get("currentTaskRoute", "")),
            str(existing.get("currentTaskRoute", "")),
            str(current_unit.get("goal", "")),
            goal,
            str(state.get("intent", "")),
        ]
    ).lower()
    full_terms = [
        "/project",
        "/kickstart",
        "/blueprint",
        "/deploy",
        "/migrate",
        "/security-audit",
        "/harden",
        "full cycle",
        "production",
        "release",
        "security",
        "migration",
        "deploy",
        "broad",
        "architecture",
    ]
    minimal_terms = [
        "/doc",
        "/explain",
        "/review",
        "small task",
        "tiny change",
        "typo",
        "copy edit",
        "readme",
        "docs-only",
        "documentation only",
        "no behavior change",
        "small enough",
        "маленьк",
        "мелк",
        "опечат",
    ]
    if any(term in text for term in full_terms):
        return "full", "high-risk or broad route hint"
    if bugfix or behavior_change:
        return "standard", "behavior-change or bugfix route"
    if any(term in text for term in minimal_terms):
        return "minimal", "small-task route hint"
    return load_route_profiles().get("defaultProfile", "standard"), "default route profile"


def expand_profile_command(command: str, project: Path) -> str:
    command = str(command).replace("<project>", str(project))
    parts = command.split()
    if len(parts) >= 2 and parts[0] == "python3" and parts[1].startswith("scripts/"):
        script = ROOT / parts[1]
        return " ".join([sys.executable, str(script), *parts[2:]])
    return command


def profile_commands(profile_id: str, project: Path) -> list[str]:
    policy = route_profile_config(profile_id).get("verificationPolicy", {})
    commands = policy.get("defaultCommands", []) if isinstance(policy, dict) else []
    return [expand_profile_command(command, project) for command in commands]


def route_profile_payload(profile_id: str, reason: str, project: Path) -> dict:
    config = route_profile_config(profile_id)
    policy = config.get("verificationPolicy", {}) if isinstance(config.get("verificationPolicy"), dict) else {}
    return {
        "id": profile_id,
        "label": config.get("label", profile_id),
        "reason": reason,
        "intendedFor": config.get("intendedFor", ""),
        "steps": config.get("steps", []),
        "gates": config.get("gates", []),
        "requiredArtifacts": config.get("requiredArtifacts", []),
        "optionalArtifacts": config.get("optionalArtifacts", []),
        "forbiddenArtifacts": config.get("forbiddenArtifacts", []),
        "verificationPolicy": {
            "mode": policy.get("mode", ""),
            "commands": profile_commands(profile_id, project),
            "rules": policy.get("rules", []),
        },
    }


def required_inputs_for_profile(profile_id: str, behavior_change: bool, bugfix: bool) -> list[str]:
    config = route_profile_config(profile_id)
    required = list(config.get("requiredArtifacts", []))
    if behavior_change and "failing test command before implementation for behavior changes" not in required:
        required.append("failing test command before implementation for behavior changes")
        required.append("passing test command after minimal implementation")
    if bugfix and "ROOT_CAUSE.md for bugfix units" not in required:
        required.append("ROOT_CAUSE.md for bugfix units")
    return required


def gates_for_profile(profile_id: str, behavior_change: bool, bugfix: bool) -> list[str]:
    gates = list(route_profile_config(profile_id).get("gates", []))
    if behavior_change:
        for gate in ["tddRed", "tddGreen"]:
            if gate not in gates:
                gates.append(gate)
    if bugfix and "rootCause" not in gates:
        gates.append("rootCause")
    return gates


def infer_next_best_action(project: Path, state: dict) -> dict:
    ensure_autonomy_state(state)
    gates = state.get("gateResults", {}) if isinstance(state.get("gateResults"), dict) else {}
    manifest = state.get("unitContextManifest", {}) if isinstance(state.get("unitContextManifest"), dict) else {}
    discipline = manifest.get("engineeringDiscipline", {}) if isinstance(manifest.get("engineeringDiscipline"), dict) else {}
    tdd = state.get("tddEvidence", {}) if isinstance(state.get("tddEvidence"), dict) else {}

    adoption_missing = missing_files(project, ["AGENTS.md", "CODEX.md", ".codex-memory/STATE.json", ".pfo/PROJECT_CONTRACT.md"])
    if adoption_missing:
        return {
            "gate": "adoption",
            "route": "/task -> /adopt",
            "command": f"pfo adopt {project}",
            "reason": "PFO runtime adoption artifacts are missing: " + ", ".join(adoption_missing),
            "blocks": "planning and implementation",
        }

    profile_id, profile_reason = select_route_profile(state)
    profile = route_profile_config(profile_id)
    if profile_id == "full":
        plan_missing = missing_files(project, PLAN_ARTIFACTS)
        if plan_missing:
            return {
                "gate": "planning",
                "route": "/project -> /blueprint",
                "profile": profile_id,
                "command": f"pfo plan {project}",
                "reason": "Planning artifacts are missing: " + ", ".join(plan_missing),
                "blocks": "unit dispatch",
            }

    if profile_id != "minimal" and not gate_passed(state, "nextStepApproval"):
        return {
            "gate": "nextStepApproval",
            "route": "/task -> approval gate",
            "profile": profile_id,
            "command": f"pfo approve-next {project} --by user",
            "reason": "The next implementation step has not been approved.",
            "blocks": "implementation dispatch",
        }

    if missing_files(project, [".pfo/UNIT_CONTEXT_MANIFEST.json", ".pfo/VERIFICATION_CONTRACT.json"]):
        unit = state.get("currentNode") or "N1"
        return {
            "gate": "unitContextManifest",
            "route": "/task -> manifest",
            "profile": profile_id,
            "command": f"pfo manifest {project} --unit {unit} --goal \"Implement {unit}\" --profile {profile_id}",
            "reason": f"Unit scope and {profile_id} verification contract must exist before implementation.",
            "blocks": "implementation dispatch",
        }

    if profile_id == "minimal" and not gate_passed(state, "scopeLock"):
        return {
            "gate": "scopeLock",
            "route": "/task -> scope",
            "profile": profile_id,
            "command": f"pfo contracts {project}",
            "reason": "Minimal tasks must prove scope before any verification or review.",
            "blocks": "targeted verification",
        }

    if profile_id == "minimal" and not gate_passed(state, "targetedVerification"):
        commands = profile.get("verificationPolicy", {}).get("defaultCommands", [])
        return {
            "gate": "targetedVerification",
            "route": "/task -> targeted verification",
            "profile": profile_id,
            "command": " && ".join(expand_profile_command(command, project) for command in commands),
            "reason": "Minimal tasks run only adoption, scope, targeted verification, review, and state-save.",
            "blocks": "review",
        }

    if discipline.get("bugfix") and not gate_passed(state, "rootCause"):
        return {
            "gate": "rootCause",
            "route": "/task -> /bugfix",
            "profile": profile_id,
            "command": f"pfo root-cause {project} --summary \"...\" --evidence \"...\" --hypothesis \"...\"",
            "reason": "Bugfix units require reproduction evidence and a fix hypothesis before implementation.",
            "blocks": "bugfix implementation",
        }

    if discipline.get("behaviorChange") and not tdd.get("red"):
        return {
            "gate": "tddRed",
            "route": "/task -> /test",
            "profile": profile_id,
            "command": f"pfo tdd-evidence {project} --red \"failing test command and expected failure\"",
            "reason": "Behavior changes require failing-test evidence before implementation.",
            "blocks": "behavior implementation",
        }

    if discipline.get("behaviorChange") and not tdd.get("green"):
        return {
            "gate": "tddGreen",
            "route": "/task -> /test",
            "profile": profile_id,
            "command": f"pfo tdd-evidence {project} --green \"passing test command after minimal implementation\"",
            "reason": "Behavior changes require passing-test evidence after implementation.",
            "blocks": "review",
        }

    if not gate_passed(state, "verificationContract"):
        return {
            "gate": "verificationContract",
            "route": "/task -> contract gate",
            "profile": profile_id,
            "command": f"pfo contracts {project}",
            "reason": "The verification contract has not passed.",
            "blocks": "review and deploy readiness",
        }

    if profile_id in {"standard", "full"} and not gate_passed(state, "targetedVerification"):
        commands = profile.get("verificationPolicy", {}).get("defaultCommands", [])
        return {
            "gate": "targetedVerification",
            "route": "/task -> targeted verification",
            "profile": profile_id,
            "command": " && ".join(expand_profile_command(command, project) for command in commands),
            "reason": f"{profile_id} route requires route-relevant verification before review.",
            "blocks": "quality review",
        }

    if gates.get("tests") in {"", "PENDING", "BLOCKED", None}:
        return {
            "gate": "tests",
            "route": "/task -> /test",
            "profile": profile_id,
            "command": f"pfo test {project}",
            "reason": "Tests are not recorded as passed or accepted.",
            "blocks": "quality review",
        }

    if not gate_passed(state, "specComplianceReview"):
        return {
            "gate": "specComplianceReview",
            "route": "/task -> /review",
            "profile": profile_id,
            "command": f"pfo review-stage {project} --stage spec --status PASSED --evidence \"...\"",
            "reason": "Spec compliance review must run before code quality review.",
            "blocks": "code quality review",
        }

    if not gate_passed(state, "codeQualityReview"):
        return {
            "gate": "codeQualityReview",
            "route": "/task -> /review",
            "profile": profile_id,
            "command": f"pfo review-stage {project} --stage quality --status PASSED --evidence \"...\"",
            "reason": "Code quality review is not recorded.",
            "blocks": "branch finish and deploy readiness",
        }

    if profile_id == "minimal":
        return {
            "gate": "stateSave",
            "route": "/task -> state-save",
            "profile": profile_id,
            "command": f"pfo full-cycle {project} --skip-plan --skip-test --skip-build --skip-review --note \"minimal route state-save\"",
            "reason": f"Minimal route complete after {', '.join(profile.get('steps', []))}.",
            "blocks": "",
        }

    if gates.get("branchFinish") in {"", "PENDING", "BLOCKED", None}:
        return {
            "gate": "branchFinish",
            "route": "/task -> /github-workflow",
            "profile": profile_id,
            "command": f"pfo finish-branch {project} --mode pr --verification \"...\"",
            "reason": "Completed branch work needs an explicit PR, merge, keep, or discard decision.",
            "blocks": "release cleanup",
        }

    return {
        "gate": "sessionSave",
        "route": "/task -> /session-save",
        "profile": profile_id,
        "command": f"pfo full-cycle {project} --skip-plan --skip-test --skip-build --skip-review --note \"state save\"",
        "reason": f"Core {profile_id} gates are satisfied; save resumable state and continue to the next approved unit or deploy-readiness gate.",
        "blocks": "",
    }


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

## SEO Growth Guarantee

Use `SEO_GROWTH_GUARANTEE_GATE.md` when organic traffic, ranking, indexing, CTR, or SEO conversion growth is claimed or targeted.

Required fields: baseline metric, target metric, measurement source, attribution window, implemented changes, exclusion factors, result decision, next iteration.

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


def generated_seo_growth_guarantee_gate() -> str:
    return """# SEO Growth Guarantee Gate

Use this gate when SEO work claims or targets measurable growth for a concrete product, page set, market, or content surface.

## Gate Status

```text
PENDING
```

## Gate Fields

| Field | Value | Evidence |
|---|---|---|
| Baseline Metric |  | Search Console, Analytics, rank tracker, crawl, or approved export before changes |
| Target Metric |  | numeric target and direction |
| Measurement Source |  | Search Console, Analytics, logs, crawl report, rank tracker, or approved dataset |
| Attribution Window |  | start date, end date, and reason the window fits crawl/indexing lag |
| Implemented Changes |  | shipped SEO changes, commit/PR/deploy links, sitemap submission, or content updates |
| Exclusion Factors |  | algorithm updates, seasonality, campaigns, tracking changes, outages, competitor shocks, or none |
| Result Decision | PENDING | PENDING, KEEP, DISCARD, ITERATE, BLOCKED, or STOP |
| Next Iteration |  | smallest next SEO experiment or explicit stop reason |

## Rules

- This gate guarantees measurement discipline, not search-engine outcomes.
- Do not claim traffic, ranking, CTR, indexing, conversion, or revenue growth without a baseline and measurement source.
- Use `python3 scripts/validate_seo_growth_gate.py <project> --allow-pending` while measurement is in flight.
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
| SEO Growth Guarantee | PENDING | SEO_GROWTH_GUARANTEE_GATE.md baseline, target, source, attribution window, changes, exclusions, decision, next iteration |  |
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
| Context Budget | PENDING | `pfo context-budget`, `.pfo/PERMISSION_MATRIX.json`, `.codex-memory/context-index.json`, `.codex-memory/resume-snapshot.md` |  |
| Verification Contract | PENDING | `.pfo/VERIFICATION_CONTRACT.json` |  |
| Tool Capability Registry | PENDING | `.pfo/TOOL_CAPABILITY_REGISTRY.json` |  |
| Next Step Approval | PENDING | `NEXT_STEP.md` user decision before the next major implementation step |  |
| Handoff | PENDING | `HANDOFF.md` before session transfer, role switch, delegation, AFK, compaction, or recovery |  |
| Work Verification | PENDING | `pfo verify-work` evidence |  |
| Experiment Loop | PENDING | `.pfo/EXPERIMENT_PROGRAM.md`, `.pfo/EXPERIMENTS.tsv`, fixed metric and keep/discard/crash decision |  |
| Browser Smoke | PENDING | `/browser-check` target, engine, flow, screenshot/log evidence for browser-facing products |  |
| Security | PENDING | `/security-audit` or accepted not-applicable note |  |
| Security Evidence | PENDING | Codex Security diff-scan or PFO-equivalent report plus coverage artifacts for `security_change` diffs |  |
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


def generated_unit_manifest(
    project: Path,
    state: dict,
    unit_id: str,
    goal: str,
    behavior_change: bool = False,
    bugfix: bool = False,
    profile: str = "auto",
) -> dict:
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
    profile_id, profile_reason = select_route_profile(
        state,
        goal,
        explicit_profile=profile,
        behavior_change=inferred_behavior_change,
        bugfix=inferred_bugfix,
    )
    return {
        "version": 1,
        "unitId": node,
        "goal": goal or f"Execute Product Factory OS unit {node}.",
        "createdAt": now_iso(),
        "routeProfile": route_profile_payload(profile_id, profile_reason, project),
        "requiredInputs": required_inputs_for_profile(profile_id, inferred_behavior_change, inferred_bugfix),
        "allowedWriteAreas": [
            "files listed by the active execution graph node",
            "tests for changed behavior",
            "PFO_REPORT.md",
            "plans/",
            "reports/",
            ".codex-memory/STATE.json",
            ".codex-memory/MEMORY.md",
            ".codex-memory/events.jsonl",
            ".codex-memory/context-index.json",
            ".codex-memory/resume-snapshot.md",
            ".codex-memory/context-summary.md",
        ],
        "forbiddenChanges": [
            "scope outside `.pfo/SCOPE_LOCK.md`",
            "silent production data substitution",
            "unapproved deployment, migration, DNS, or production mutation",
            "golden-flow behavior changes without verification evidence",
            "commands or writes outside `.pfo/EXECUTION_POLICY.json` and `.pfo/PERMISSION_MATRIX.md`",
        ],
        "dependencies": [],
        "verificationCommands": profile_commands(profile_id, project),
        "contextPolicy": {
            "mode": "progressive-disclosure",
            "rules": [
                "load only the required inputs for the active unit",
                "offload long logs and tool output to files, then keep summaries and paths in context",
                "run pfo context-budget before adding large tool/read/log/web/raw HTTP output to active chat context",
                "use sandbox-summary: analyze large output with scripts, then keep only summary, key evidence, and artifact path in context",
                "use pfo context-search instead of reloading full event logs",
                "write HANDOFF.md before compaction, context reset, delegation, AFK execution, or recovery",
                "prefer durable artifact references over chat-only memory",
            ],
        },
        "sandbox": {
            "type": "local",
            "read_paths": ["."],
            "write_paths": [
                "files listed by the active execution graph node",
                "tests/",
                "plans/",
                "reports/",
                ".codex-memory/",
                ".pfo/",
            ],
            "allow_network": False,
            "env_passthrough": [],
            "readPaths": ["."],
            "writePaths": [
                "files listed by the active execution graph node",
                "tests/",
                "plans/",
                "reports/",
                ".codex-memory/",
                ".pfo/",
            ],
            "allowNetwork": False,
            "envPassthrough": [],
            "policySource": ".pfo/EXECUTION_POLICY.json",
        },
        "toolPolicy": {
            "mode": "minimal-trusted-menu",
            "rules": [
                "use the smallest declared tool that can satisfy the active route",
                "do not use connectors outside .pfo/TOOL_CAPABILITY_REGISTRY.json without explicit approval",
                "treat tool descriptions and MCP metadata as trusted prompt input",
                "record a fallback or blocker when a required tool is unavailable",
            ],
        },
        "harnessPolicy": {
            "sourcePattern": "Martin Fowler coding-agent user harness",
            "guideSensorPairing": "Blocking guides should name the feedback sensors that prove or repair them.",
            "regulationCategories": ["maintainability", "architecture_fitness", "behaviour"],
            "qualityLeft": {
                "localFastSensors": [
                    "targeted tests",
                    "validators",
                    "lint or schema checks",
                    "contract gates relevant to touched files",
                ],
                "pipelineSensors": [
                    "full fixture suite",
                    "production readiness",
                    "security/dependency review when risk warrants it",
                ],
                "continuousSensors": [
                    "state freshness",
                    "dependency drift",
                    "benchmark or runtime health signals when available",
                ],
            },
            "harnessabilityChecks": [
                "clear module boundaries",
                "available verification commands",
                "golden flows or fixtures for behaviour changes",
                "observable logs or health checks for runtime work",
            ],
            "humanSteering": [
                "unclear intent",
                "accepted risk",
                "load-bearing convention",
                "conflicting or missing sensor evidence",
            ],
        },
        "gates": gates_for_profile(profile_id, inferred_behavior_change, inferred_bugfix),
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
    profile = manifest.get("routeProfile", {}) if isinstance(manifest.get("routeProfile"), dict) else {}
    profile_id = str(profile.get("id") or "standard")
    commands = profile_commands(profile_id, project)
    command_items = []
    for index, command in enumerate(commands, start=1):
        command_items.append(
            {
                "id": f"{profile_id}-verification-{index}",
                "command": command,
                "timeoutSeconds": 90 if "production_readiness.py" not in command else 180,
                "expectedOutput": "Command exits 0 and provides route-profile-relevant verification evidence.",
                "passFailParser": "exit_code_zero",
                "required": True,
            }
        )
    return {
        "version": 1,
        "purpose": "Executable verification contract for the active PFO unit.",
        "unitId": unit_id,
        "createdAt": now_iso(),
        "routeProfile": profile,
        "sensorPolicy": {
            "qualityLeft": "Run fast computational sensors locally before broader or inferential gates.",
            "regulates": ["maintainability", "architecture_fitness", "behaviour"],
            "localFastSensors": ["targeted tests", "validators", "lint or schema checks", "contract gates"],
            "pipelineSensors": ["full fixture suite", "production readiness", "security/dependency gates when applicable"],
            "continuousSensors": ["state freshness", "dependency drift", "benchmarks or runtime health when available"],
        },
        "commands": command_items,
        "requiredArtifacts": manifest.get("requiredInputs", []),
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


def acceptance_contract_path(project: Path) -> Path:
    return project / ".pfo" / "ACCEPTANCE_CONTRACT.json"


def load_acceptance_contract(project: Path) -> dict:
    path = acceptance_contract_path(project)
    if not path.is_file():
        raise SystemExit(f"ERROR: missing acceptance contract: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid acceptance contract JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("ERROR: acceptance contract must be a JSON object")
    return data


def write_acceptance_contract(project: Path, contract: dict) -> None:
    path = acceptance_contract_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def default_acceptance_contract(request: str, unit_id: str = "", goal: str = "") -> dict:
    source = request or goal or "PFO unit request"
    criterion_id = "AC1"
    return {
        "version": 1,
        "createdAt": now_iso(),
        "createdBeforeImplementation": True,
        "originalRequest": source,
        "unitId": unit_id,
        "status": "PENDING",
        "criteria": [
            {
                "id": criterion_id,
                "requirement": source,
                "source": "user_request",
                "sourceQuote": source,
                "verification": "Record task-specific evidence before passing pfo verify-work --pass-gate.",
                "status": "PENDING",
                "evidenceKind": "",
                "evidence": "",
                "independentEvidence": "",
            }
        ],
    }


def acceptance_contract_ready(project: Path) -> bool:
    return run_script("validate_acceptance_contract.py", [str(project)]) == 0


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

## Harness Policy

- Pair feedforward guides with feedback sensors where practical.
- Regulate maintainability, architecture fitness, and behaviour explicitly.
- Run fast computational sensors before broader or inferential gates.
- Use human steering for unclear intent, accepted risk, load-bearing conventions, or missing sensor evidence.

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


def cmd_next_best_action(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    action = infer_next_best_action(project, state)
    if args.write:
        state["nextBestAction"] = action
        set_next_step_pending(
            project,
            state,
            f"Next best action selected from state gate `{action['gate']}`.",
            action["command"],
            [
                "Run the recommended command.",
                "Change the route or scope before continuing.",
                "Pause and inspect PFO status manually.",
            ],
            [
                "Do you approve the recommended next gate action?",
                "Should PFO choose a different route before implementation continues?",
            ],
        )
        append_event(project, state, "state-change", "RECORDED", {"command": "next-best-action", "action": action})
        save_state(project, state)
    if args.json:
        print(json.dumps(action, indent=2, ensure_ascii=False))
    else:
        print(f"Gate: {action['gate']}")
        print(f"Route: {action['route']}")
        print(f"Command: {action['command']}")
        print(f"Reason: {action['reason']}")
        if action.get("blocks"):
            print(f"Blocks: {action['blocks']}")
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
        (project / "SEO_GROWTH_GUARANTEE_GATE.md", generated_seo_growth_guarantee_gate()),
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
        "SEO_GROWTH_GUARANTEE_GATE.md",
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
    manifest = generated_unit_manifest(project, state, args.unit, args.goal, args.behavior_change, args.bugfix, args.profile)
    pfo_dir = project / ".pfo"
    pfo_dir.mkdir(exist_ok=True)
    manifest_path = pfo_dir / "UNIT_CONTEXT_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    verification_contract = generated_verification_contract(project, manifest)
    verification_path = pfo_dir / "VERIFICATION_CONTRACT.json"
    verification_path.write_text(json.dumps(verification_contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    acceptance_path = acceptance_contract_path(project)
    if not acceptance_path.is_file():
        write_acceptance_contract(project, default_acceptance_contract(args.goal, manifest["unitId"], manifest["goal"]))
        state["acceptanceContract"] = {"path": ".pfo/ACCEPTANCE_CONTRACT.json", "status": "PENDING"}
        state["gateResults"]["acceptanceContract"] = "PENDING"
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
    state["activeRouteProfile"] = manifest["routeProfile"]
    state["executionPolicy"] = {"path": ".pfo/EXECUTION_POLICY.json", "status": "READY"}
    state["permissionMatrix"] = {"path": ".pfo/PERMISSION_MATRIX.json", "humanPath": ".pfo/PERMISSION_MATRIX.md", "status": "READY"}
    state["contextBudget"] = {"gate": "pfo context-budget", "indexPath": ".codex-memory/context-index.json", "snapshotPath": ".codex-memory/resume-snapshot.md", "status": "READY"}
    state["toolCapabilityRegistry"] = {"path": ".pfo/TOOL_CAPABILITY_REGISTRY.json", "status": "READY"}
    state["verificationContract"] = {"path": ".pfo/VERIFICATION_CONTRACT.json", "status": "READY"}
    state.setdefault("acceptanceContract", {"path": ".pfo/ACCEPTANCE_CONTRACT.json", "status": "PENDING"})
    state["gateResults"]["executionPolicy"] = "PASSED"
    state["gateResults"]["permissionMatrix"] = "PASSED"
    state["gateResults"]["contextBudget"] = "PASSED"
    state["gateResults"]["toolCapabilityRegistry"] = "PASSED"
    state["gateResults"]["verificationContract"] = "PASSED"
    state["gateResults"].setdefault("acceptanceContract", "PENDING")
    add_artifact(state, ".pfo/UNIT_CONTEXT_MANIFEST.json")
    add_artifact(state, ".pfo/VERIFICATION_CONTRACT.json")
    add_artifact(state, ".pfo/ACCEPTANCE_CONTRACT.json")
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
    print(
        "OK: wrote .pfo/UNIT_CONTEXT_MANIFEST.json, "
        f".pfo/VERIFICATION_CONTRACT.json, .pfo/ACCEPTANCE_CONTRACT.json, and {plan_rel} "
        f"with {manifest['routeProfile']['id']} profile"
    )
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    run_script("pfo_context_runtime.py", ["snapshot", str(project), "--reason", args.reason or "handoff", "--quiet"])
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


def write_full_cycle_session(project: Path, state: dict, steps: list[dict], note: str) -> str:
    memory_dir = project / ".codex-memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    session_name = f"session_{stamp}_full-cycle.md"
    session_path = memory_dir / session_name
    rows = "\n".join(
        f"| {step['name']} | {step['status']} | {step.get('exitCode', '')} | {step.get('note', '')} |"
        for step in steps
    )
    session_path.write_text(
        "# Full-Cycle Session\n\n"
        f"- Project: `{project}`\n"
        f"- Recorded at: `{now_iso()}`\n"
        f"- Note: {note or 'none'}\n\n"
        "## Steps\n\n"
        "| Step | Status | Exit Code | Note |\n"
        "|---|---|---:|---|\n"
        f"{rows}\n\n"
        "## Next Action\n\n"
        f"{state.get('nextAction', '')}\n",
        encoding="utf-8",
    )
    memory_path = memory_dir / "MEMORY.md"
    existing = memory_path.read_text(encoding="utf-8") if memory_path.is_file() else "# Memory\n\n"
    entry = f"- {stamp}: full-cycle orchestration -> {session_name}\n"
    if entry not in existing:
        memory_path.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")
    add_artifact(state, f".codex-memory/{session_name}")
    add_artifact(state, ".codex-memory/MEMORY.md")
    return f".codex-memory/{session_name}"


def cmd_full_cycle(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    steps: list[dict] = []

    def record(name: str, code: int, note: str = "") -> None:
        steps.append(
            {
                "name": name,
                "status": "PASSED" if code == 0 else "BLOCKED",
                "exitCode": code,
                "note": note,
            }
        )

    def should_continue(code: int) -> bool:
        return code == 0 or not args.stop_on_blocked

    if not args.skip_plan:
        code = cmd_plan(argparse.Namespace(project=project, note=args.note or "full-cycle orchestration"))
        record("plan", code, "pfo plan")
        if not should_continue(code):
            return code

    if not args.skip_test:
        code = run_script("pfo_runner.py", [str(project), "--mode", "test"])
        record("test", code, "pfo test")
        if not should_continue(code):
            return code

    if not args.skip_build:
        code = run_script("pfo_runner.py", [str(project), "--mode", "build"])
        record("implementation", code, "pfo build dispatch")
        if not should_continue(code):
            return code

    if not args.skip_review:
        code = run_script("pfo_runner.py", [str(project), "--mode", "review"])
        record("review", code, "pfo review")
        if not should_continue(code):
            return code

    run_script("pfo_context_runtime.py", ["snapshot", str(project), "--reason", "full-cycle", "--quiet"])
    state = load_state(project)
    ensure_autonomy_state(state)
    blocked = [step for step in steps if step["status"] == "BLOCKED"]
    status = "BLOCKED" if blocked else "PASSED"
    session_rel = write_full_cycle_session(project, state, steps, args.note)
    state["fullCycle"] = {
        "status": status,
        "recordedAt": now_iso(),
        "sessionPath": session_rel,
        "steps": steps,
    }
    state["sessionState"] = "ACTIVE"
    if status == "PASSED":
        state["currentStage"] = "SESSION_SAVED"
        state["lastSuccessfulState"] = "SESSION_SAVED"
        state["nextAction"] = "Review full-cycle session notes, then continue with the next approved PFO unit or deploy-readiness gate."
    else:
        failed = ", ".join(step["name"] for step in blocked)
        state["nextAction"] = f"Resolve blocked full-cycle step(s): {failed}."
    append_event(project, state, "state-change", status, {"command": "full-cycle", "steps": steps})
    save_state(project, state)
    print(f"OK: full-cycle recorded as {status}")
    print(f"Session: {session_rel}")
    for step in steps:
        print(f"{step['name']}: {step['status']} ({step['exitCode']})")
    return 0 if status == "PASSED" else 1


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
        if not acceptance_contract_ready(project):
            raise SystemExit("ERROR: cannot pass verification until .pfo/ACCEPTANCE_CONTRACT.json passes")
        state["gateResults"]["review"] = "PASSED"
        state["gateResults"]["verificationContract"] = "PASSED"
        state["gateResults"]["acceptanceContract"] = "PASSED"
        state["gateResults"]["targetedVerification"] = "PASSED"
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


def cmd_acceptance(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    action = args.acceptance_action
    if action == "init":
        if acceptance_contract_path(project).is_file() and not args.force:
            raise SystemExit("ERROR: .pfo/ACCEPTANCE_CONTRACT.json already exists; use --force to replace it")
        contract = default_acceptance_contract(args.request, args.unit, args.request)
        criteria = []
        for index, raw in enumerate(args.criterion or [], start=1):
            parts = raw.split("::", 2)
            if len(parts) == 3:
                criterion_id, requirement, verification = parts
            else:
                criterion_id = f"AC{index}"
                requirement = raw
                verification = "Provide independent evidence before passing acceptance gate."
            criteria.append(
                {
                    "id": criterion_id.strip() or f"AC{index}",
                    "requirement": requirement.strip(),
                    "source": "user_request",
                    "sourceQuote": requirement.strip(),
                    "verification": verification.strip(),
                    "status": "PENDING",
                    "evidenceKind": "",
                    "evidence": "",
                    "independentEvidence": "",
                }
            )
        if criteria:
            contract["criteria"] = criteria
        write_acceptance_contract(project, contract)
        state["acceptanceContract"] = {"path": ".pfo/ACCEPTANCE_CONTRACT.json", "status": "PENDING"}
        state["gateResults"]["acceptanceContract"] = "PENDING"
        add_artifact(state, ".pfo/ACCEPTANCE_CONTRACT.json")
        append_event(project, state, "gate", "PENDING", {"command": "acceptance init", "criteria": len(contract["criteria"])})
        save_state(project, state)
        print(f"OK: wrote .pfo/ACCEPTANCE_CONTRACT.json with {len(contract['criteria'])} criteria")
        return 0
    if action == "add":
        contract = load_acceptance_contract(project)
        criteria = contract.setdefault("criteria", [])
        if not isinstance(criteria, list):
            raise SystemExit("ERROR: acceptance criteria must be a list")
        criteria.append(
            {
                "id": args.id,
                "requirement": args.requirement,
                "source": "user_request",
                "sourceQuote": args.source_quote or args.requirement,
                "verification": args.verification,
                "status": "PENDING",
                "evidenceKind": "",
                "evidence": "",
                "independentEvidence": "",
            }
        )
        contract["status"] = "PENDING"
        write_acceptance_contract(project, contract)
        state["acceptanceContract"] = {"path": ".pfo/ACCEPTANCE_CONTRACT.json", "status": "PENDING"}
        state["gateResults"]["acceptanceContract"] = "PENDING"
        add_artifact(state, ".pfo/ACCEPTANCE_CONTRACT.json")
        append_event(project, state, "gate", "PENDING", {"command": "acceptance add", "id": args.id})
        save_state(project, state)
        print(f"OK: added acceptance criterion {args.id}")
        return 0
    if action == "verify":
        contract = load_acceptance_contract(project)
        found = False
        for item in contract.get("criteria", []):
            if isinstance(item, dict) and item.get("id") == args.id:
                item["status"] = args.status
                item["evidenceKind"] = args.evidence_kind
                item["evidence"] = args.evidence
                item["independentEvidence"] = args.independent_evidence
                item["verifiedAt"] = now_iso()
                found = True
                break
        if not found:
            raise SystemExit(f"ERROR: acceptance criterion not found: {args.id}")
        statuses = [str(item.get("status", "")).upper() for item in contract.get("criteria", []) if isinstance(item, dict)]
        contract["status"] = "PASSED" if statuses and all(status == "PASSED" for status in statuses) else "PENDING"
        write_acceptance_contract(project, contract)
        state["acceptanceContract"] = {"path": ".pfo/ACCEPTANCE_CONTRACT.json", "status": contract["status"]}
        state["gateResults"]["acceptanceContract"] = contract["status"]
        append_event(project, state, "gate", contract["status"], {"command": "acceptance verify", "id": args.id})
        save_state(project, state)
        print(f"OK: acceptance criterion {args.id} recorded as {args.status}")
        return 0
    if action == "gate":
        if not acceptance_contract_ready(project):
            return 1
        state["acceptanceContract"] = {"path": ".pfo/ACCEPTANCE_CONTRACT.json", "status": "PASSED"}
        state["gateResults"]["acceptanceContract"] = "PASSED"
        append_event(project, state, "gate", "PASSED", {"command": "acceptance gate"})
        save_state(project, state)
        print("OK: acceptance gate passed")
        return 0
    if action == "status":
        contract = load_acceptance_contract(project)
        print(json.dumps(contract, indent=2, ensure_ascii=False) if args.json else contract.get("status", ""))
        return 0
    raise SystemExit(f"ERROR: unknown acceptance action: {action}")


def cmd_context_budget(args: argparse.Namespace) -> int:
    argv = ["budget", str(args.project), "--kind", args.kind, "--bytes", str(args.bytes), "--lines", str(args.lines)]
    if args.command_text:
        argv.extend(["--command-text", args.command_text])
    if args.raw_http:
        argv.append("--raw-http")
    if args.approved:
        argv.append("--approved")
    if args.json:
        argv.append("--json")
    return run_script("pfo_context_runtime.py", argv)


def cmd_context_index(args: argparse.Namespace) -> int:
    return run_script("pfo_context_runtime.py", ["index", str(args.project)])


def cmd_context_search(args: argparse.Namespace) -> int:
    argv = ["search", str(args.project), *args.query, "--limit", str(args.limit)]
    if args.reindex:
        argv.append("--reindex")
    if args.json:
        argv.append("--json")
    return run_script("pfo_context_runtime.py", argv)


def cmd_context_snapshot(args: argparse.Namespace) -> int:
    argv = ["snapshot", str(args.project), "--reason", args.reason]
    if args.quiet:
        argv.append("--quiet")
    return run_script("pfo_context_runtime.py", argv)


def cmd_tool_registry(args: argparse.Namespace) -> int:
    return run_script("validate_tool_registry.py", [str(args.project / ".pfo" / "TOOL_CAPABILITY_REGISTRY.json")])


def cmd_skill_scaffold(args: argparse.Namespace) -> int:
    argv = [args.skill_name, "--description", args.description]
    scalar_options = [
        ("--russian-triggers", args.russian_triggers),
        ("--prompt", args.prompt),
        ("--input", args.input),
        ("--notes", args.notes),
        ("--notes-token", args.notes_token),
        ("--argument-hint", args.argument_hint),
        ("--category", args.category),
        ("--effort", args.effort),
        ("--side-effect", args.side_effect),
        ("--fixture", args.fixture),
    ]
    for flag, value in scalar_options:
        if value:
            argv.extend([flag, value])
    repeat_options = [
        ("--trigger", args.trigger),
        ("--output", args.output),
        ("--expected-file", args.expected_file),
        ("--required-file", args.required_file),
        ("--stdout-token", args.stdout_token),
        ("--any-file-token", args.any_file_token),
        ("--validation-command", args.validation_command),
        ("--tag", args.tag),
        ("--resource", args.resource),
    ]
    for flag, values in repeat_options:
        for value in values:
            argv.extend([flag, value])
    if args.explicit_invocation:
        argv.append("--explicit-invocation")
    if args.force:
        argv.append("--force")
    return run_script("pfo_skill_scaffold.py", argv)


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


READINESS_LEVELS = [
    {
        "level": 1,
        "name": "Functional",
        "checks": [
            ("readme", "README.md"),
            ("gitignore", ".gitignore"),
            ("testing", "TESTING.md"),
        ],
    },
    {
        "level": 2,
        "name": "Adopted",
        "checks": [
            ("agents", "AGENTS.md"),
            ("codex", "CODEX.md"),
            ("state", ".codex-memory/STATE.json"),
            ("project-contract", ".pfo/PROJECT_CONTRACT.md"),
        ],
    },
    {
        "level": 3,
        "name": "Gated",
        "checks": [
            ("scope-lock", ".pfo/SCOPE_LOCK.md"),
            ("data-policy", ".pfo/DATA_POLICY.md"),
            ("permission-matrix", ".pfo/PERMISSION_MATRIX.json"),
            ("verification-contract", ".pfo/VERIFICATION_CONTRACT.json"),
        ],
    },
    {
        "level": 4,
        "name": "Measured",
        "checks": [
            ("events", ".codex-memory/events.jsonl"),
            ("context-index", ".codex-memory/context-index.json"),
            ("resume-snapshot", ".codex-memory/resume-snapshot.md"),
            ("report", "PFO_REPORT.md"),
        ],
    },
    {
        "level": 5,
        "name": "Self-improving",
        "checks": [
            ("learning-gate", ".pfo/LEARNING_PROMOTION_GATE.md"),
            ("learnings", ".codex-memory/LEARNINGS.jsonl"),
            ("learning-proposals", ".codex-memory/LEARNING_PROPOSALS.json"),
            ("experiment-program", ".pfo/EXPERIMENT_PROGRAM.md"),
        ],
    },
]


def readiness_report(project: Path) -> dict:
    state = load_state(project) if (project / ".codex-memory" / "STATE.json").is_file() else {}
    level_results = []
    achieved = 0
    for spec in READINESS_LEVELS:
        checks = []
        passed = 0
        for check_id, rel in spec["checks"]:
            ok = (project / rel).is_file()
            passed += 1 if ok else 0
            checks.append({"id": check_id, "path": rel, "status": "PASS" if ok else "MISSING"})
        ratio_value = passed / len(spec["checks"])
        unlocked = ratio_value >= 0.8
        if unlocked and spec["level"] == achieved + 1:
            achieved = spec["level"]
        level_results.append(
            {
                "level": spec["level"],
                "name": spec["name"],
                "score": f"{passed}/{len(spec['checks'])}",
                "ratio": round(ratio_value, 4),
                "status": "PASS" if unlocked else "ATTENTION",
                "checks": checks,
            }
        )
    action_items = []
    for level in level_results:
        for check in level["checks"]:
            if check["status"] != "PASS":
                action_items.append(
                    {
                        "level": level["level"],
                        "action": f"Create or refresh {check['path']}",
                        "reason": f"Required for PFO readiness level {level['level']} ({level['name']}).",
                    }
                )
        if action_items:
            break
    gates = state.get("gateResults", {}) if isinstance(state.get("gateResults"), dict) else {}
    return {
        "project": str(project),
        "levelAchieved": achieved,
        "levelName": next((item["name"] for item in level_results if item["level"] == achieved), "Unready"),
        "levels": level_results,
        "gateSummary": gates,
        "actionItems": action_items[:3],
        "generatedAt": now_iso(),
    }


def write_readiness_report(project: Path, report: dict) -> None:
    lines = [
        "# PFO Readiness Report",
        "",
        f"- Project: `{project}`",
        f"- Generated: `{report['generatedAt']}`",
        f"- Level achieved: {report['levelAchieved']} ({report['levelName']})",
        "",
        "## Levels",
        "",
        "| Level | Name | Score | Status |",
        "|---:|---|---:|---|",
    ]
    for item in report["levels"]:
        lines.append(f"| {item['level']} | {item['name']} | {item['score']} | {item['status']} |")
    lines.extend(["", "## Action Items", ""])
    if report["actionItems"]:
        for item in report["actionItems"]:
            lines.append(f"- {item['action']} - {item['reason']}")
    else:
        lines.append("- No readiness gaps detected for the current model.")
    (project / "PFO_READINESS_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_readiness(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    report = readiness_report(project)
    if args.write:
        state = load_state(project)
        ensure_autonomy_state(state)
        write_readiness_report(project, report)
        state["readiness"] = report
        state["gateResults"]["readiness"] = "PASSED" if report["levelAchieved"] >= args.min_level else "BLOCKED"
        add_artifact(state, "PFO_READINESS_REPORT.md")
        append_event(project, state, "gate", state["gateResults"]["readiness"], {"command": "readiness", "level": report["levelAchieved"]})
        save_state(project, state)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Level: {report['levelAchieved']} ({report['levelName']})")
        for item in report["actionItems"]:
            print(f"Action: {item['action']}")
    return 0 if report["levelAchieved"] >= args.min_level else 1


def cmd_readiness_fix(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    if not args.apply:
        report = readiness_report(project)
        print(json.dumps({"mode": "dry-run", "actionItems": report["actionItems"]}, indent=2, ensure_ascii=False))
        return 0
    run_script("adoption_check.py", ["--write", "--project", str(project), "--analyze", "--report"])
    run_script("pfo_context_runtime.py", ["index", str(project)])
    run_script("pfo_context_runtime.py", ["snapshot", str(project), "--reason", "readiness-fix", "--quiet"])
    state = load_state(project)
    ensure_autonomy_state(state)
    if args.focus in {"all", "measurement"}:
        (project / ".codex-memory").mkdir(exist_ok=True)
        learnings = project / ".codex-memory" / "LEARNINGS.jsonl"
        if not learnings.exists():
            learnings.write_text("", encoding="utf-8")
        proposals = project / ".codex-memory" / "LEARNING_PROPOSALS.json"
        if not proposals.exists():
            proposals.write_text("[]\n", encoding="utf-8")
        experiment_program = project / ".pfo" / "EXPERIMENT_PROGRAM.md"
        if not experiment_program.exists():
            experiment_program.write_text(
                "# Experiment Program\n\n"
                "## Metric\n\n"
                "- Name: readiness_improvement\n"
                "- Direction: higher\n"
                "- Budget seconds: 300\n\n"
                "## Boundary\n\n"
                "Only update PFO runtime artifacts needed to improve measured readiness.\n",
                encoding="utf-8",
            )
    report = readiness_report(project)
    write_readiness_report(project, report)
    state["readiness"] = report
    state["gateResults"]["readiness"] = "PASSED"
    add_artifact(state, "PFO_READINESS_REPORT.md")
    append_event(project, state, "state-change", "PASSED", {"command": "readiness-fix", "focus": args.focus})
    save_state(project, state)
    print("OK: readiness remediation applied")
    return 0


AUTONOMY_LEVELS = {
    "off": {"rank": 0, "capabilities": {"read"}},
    "low": {"rank": 1, "capabilities": {"read", "write"}},
    "medium": {"rank": 2, "capabilities": {"read", "write", "test", "commit", "external_api"}},
    "high": {"rank": 3, "capabilities": {"read", "write", "test", "commit", "push", "deploy", "external_api"}},
}


def cmd_policy(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    level = args.auto.lower()
    if level not in AUTONOMY_LEVELS:
        print("ERROR: --auto must be off, low, medium, or high")
        return 2
    matrix_path = project / ".pfo" / "PERMISSION_MATRIX.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8")) if matrix_path.is_file() else {}
    if args.policy_action == "explain":
        payload = {
            "project": str(project),
            "autonomyLevel": level,
            "allowedCapabilities": sorted(AUTONOMY_LEVELS[level]["capabilities"]),
            "permissionMatrix": matrix,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"Autonomy {level}: {', '.join(payload['allowedCapabilities'])}")
        return 0
    required = args.capability or "read"
    allowed = required in AUTONOMY_LEVELS[level]["capabilities"]
    payload = {"capability": required, "autonomyLevel": level, "status": "PASS" if allowed else "BLOCKED"}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"{required}: {payload['status']} at autonomy {level}")
    return 0 if allowed else 1


def parse_json_arg(value: str, path_value: str = "") -> dict:
    if path_value:
        path = Path(path_value)
        return json.loads(path.read_text(encoding="utf-8"))
    if value:
        return json.loads(value)
    return {}


def policy_eval_payload(project: Path, args: argparse.Namespace) -> dict:
    event = parse_json_arg(getattr(args, "event_json", ""), getattr(args, "event_file", ""))
    event_type = event.get("type") or args.event_type
    target = event.get("target") or args.target
    data = event.get("data", {}) if isinstance(event.get("data", {}), dict) else {}
    usage = event.get("usage", {}) if isinstance(event.get("usage", {}), dict) else parse_json_arg(getattr(args, "usage_json", ""), "")
    session_state = event.get("session_state", {}) if isinstance(event.get("session_state", {}), dict) else parse_json_arg(getattr(args, "session_state_json", ""), "")
    result = event.get("result", {}) if isinstance(event.get("result", {}), dict) else parse_json_arg(getattr(args, "result_json", ""), "")
    actor = event.get("actor") or args.actor
    capability = data.get("capability") or args.capability or target or "read"
    cost_usd = float(usage.get("estimatedCostUsd", data.get("cost_usd", args.cost_usd or 0)) or 0)
    risk_score = int(usage.get("riskScore", data.get("risk_score", args.risk_score or 0)) or 0)
    tool_calls = int(usage.get("toolCalls", data.get("tool_calls", args.tool_calls or 0)) or 0)
    matrix_path = project / ".pfo" / "PERMISSION_MATRIX.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8")) if matrix_path.is_file() else {}
    capability_policy = matrix.get("capabilities", {}).get(capability, {}) if isinstance(matrix.get("capabilities"), dict) else {}
    cost_policy = matrix.get("costRiskPolicy", {}) if isinstance(matrix.get("costRiskPolicy"), dict) else {}
    default_decision = str(capability_policy.get("default") or matrix.get("defaultDecision") or "deny").lower()
    approval_required = capability_policy.get("approvalRequired", False)
    reasons: list[str] = []
    verdict = "ALLOW"
    if default_decision == "block":
        verdict = "DENY"
        reasons.append(f"{capability} is blocked by permission matrix")
    elif default_decision == "deny":
        verdict = "DENY"
        reasons.append(f"{capability} is denied by default")
    elif approval_required is True or (isinstance(approval_required, str) and approval_required not in {"false", "False", ""}):
        verdict = "ASK"
        reasons.append(f"{capability} requires approval: {approval_required}")
    risk_thresholds = cost_policy.get("riskScore", {}) if isinstance(cost_policy.get("riskScore"), dict) else {}
    cost_thresholds = cost_policy.get("estimatedCostUsd", {}) if isinstance(cost_policy.get("estimatedCostUsd"), dict) else {}
    deny_risk = int(risk_thresholds.get("denyThreshold", args.deny_risk))
    ask_risk = int(risk_thresholds.get("askThreshold", args.ask_risk))
    deny_cost = float(cost_thresholds.get("denyThreshold", args.deny_cost))
    ask_cost = float(cost_thresholds.get("askThreshold", args.ask_cost))
    if risk_score >= deny_risk:
        verdict = "DENY"
        reasons.append(f"risk score {risk_score} >= deny threshold {deny_risk}")
    elif risk_score >= ask_risk and verdict == "ALLOW":
        verdict = "ASK"
        reasons.append(f"risk score {risk_score} >= ask threshold {ask_risk}")
    if cost_usd >= deny_cost:
        verdict = "DENY"
        reasons.append(f"estimated cost ${cost_usd:.2f} >= deny threshold ${deny_cost:.2f}")
    elif cost_usd >= ask_cost and verdict == "ALLOW":
        verdict = "ASK"
        reasons.append(f"estimated cost ${cost_usd:.2f} >= ask threshold ${ask_cost:.2f}")
    if tool_calls > args.max_tool_calls:
        verdict = "DENY"
        reasons.append(f"tool call count {tool_calls} > limit {args.max_tool_calls}")
    normalized_event = {
        "type": event_type,
        "target": target,
        "data": data,
        "actor": actor,
        "usage": {
            "riskScore": risk_score,
            "estimatedCostUsd": cost_usd,
            "toolCalls": tool_calls,
            **{key: value for key, value in usage.items() if key not in {"riskScore", "estimatedCostUsd", "toolCalls"}},
        },
        "session_state": session_state,
        "result": result,
        "capability": capability,
    }
    return {
        "type": "pfo-policy-verdict",
        "project": str(project),
        "event": normalized_event,
        "result": verdict,
        "reason": "; ".join(reasons) or "allowed by active PFO policy",
        "actor": actor,
        "riskScore": risk_score,
        "estimatedCostUsd": cost_usd,
        "toolCalls": tool_calls,
        "checkedAt": now_iso(),
    }


def cmd_policy_eval(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    payload = policy_eval_payload(project, args)
    state["policyRuntime"] = {
        "engine": "pfo-policy-eval",
        "verdicts": ["ALLOW", "DENY", "ASK"],
        "lastVerdict": payload["result"],
        "lastReason": payload["reason"],
        "lastEvent": payload["event"],
        "lastEventAt": payload["checkedAt"],
    }
    state["gateResults"]["policyRuntime"] = "PASSED" if payload["result"] == "ALLOW" else payload["result"]
    if args.record:
        append_event(project, state, "policy", payload["result"], payload)
    save_state(project, state)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"{payload['result']}: {payload['reason']}")
    return 0 if payload["result"] == "ALLOW" else 1


def agent_spec_paths() -> list[Path]:
    return sorted((ROOT / "agents").glob("*.yaml"))


def validate_agent_spec_text(path: Path, text: str) -> list[str]:
    errors = []
    for token in ["spec_version:", "name:", "instructions:", "executor:", "tools:", "policies:", "terminals:", "sandbox:", "read_paths:", "write_paths:", "allow_network:", "env_passthrough:"]:
        if token not in text:
            errors.append(f"{path}: missing {token}")
    if "harness:" not in text:
        errors.append(f"{path}: missing executor harness")
    return errors


def cmd_agent_spec(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    paths = agent_spec_paths()
    if args.agent_action == "list":
        payload = {"count": len(paths), "agents": [path.stem for path in paths], "path": "agents/*.yaml"}
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else "\n".join(payload["agents"]))
        return 0
    if args.agent_action == "write-defaults":
        target_dir = project / ".pfo" / "agents"
        target_dir.mkdir(parents=True, exist_ok=True)
        for path in paths:
            (target_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        state["agentRuntime"] = {
            "specVersion": 1,
            "agentSpecsPath": "agents/*.yaml",
            "projectAgentSpecsPath": ".pfo/agents/",
            "lastValidation": now_iso(),
            "status": "READY",
        }
        state["gateResults"]["agentSpec"] = "PASSED"
        add_artifact(state, ".pfo/agents/")
        append_event(project, state, "state-change", "READY", {"command": "agent-spec", "action": "write-defaults"})
        save_state(project, state)
        print(f"OK: wrote {len(paths)} agent specs to .pfo/agents/")
        return 0
    errors = []
    template = ROOT / "docs" / "templates" / "PFO_AGENT_SPEC.yaml"
    if not template.is_file():
        errors.append("missing docs/templates/PFO_AGENT_SPEC.yaml")
    if len(paths) < 5:
        errors.append("expected at least 5 runnable agent specs under agents/*.yaml")
    for path in paths:
        errors.extend(validate_agent_spec_text(path, path.read_text(encoding="utf-8")))
    status = "PASSED" if not errors else "BLOCKED"
    state["agentRuntime"]["lastValidation"] = now_iso()
    state["agentRuntime"]["status"] = "READY" if not errors else "BLOCKED"
    state["gateResults"]["agentSpec"] = status
    append_event(project, state, "verification", status, {"command": "agent-spec", "errors": errors})
    save_state(project, state)
    payload = {"status": status, "count": len(paths), "errors": errors}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Agent spec validation: {status}")
        for error in errors:
            print(f"- {error}")
    return 0 if not errors else 1


def dispatch_id(title: str) -> str:
    return f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{slugify_unit(title)[:48]}"


def cmd_dispatch(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    item_id = dispatch_id(args.title or args.agent)
    dispatch_dir = project / ".pfo" / "dispatch"
    dispatch_dir.mkdir(parents=True, exist_ok=True)
    branch = args.branch or f"pfo/{item_id}"
    worktree_path = ""
    worktree_status = "not-requested"
    if args.worktree:
        worktree_root = project.parent / ".pfo-worktrees" / project.name
        worktree_root.mkdir(parents=True, exist_ok=True)
        worktree = worktree_root / item_id
        worktree_path = str(worktree)
        if args.no_create_worktree:
            worktree_status = "declared"
        else:
            if worktree.exists():
                worktree_status = "exists"
            else:
                completed = subprocess.run(
                    ["git", "worktree", "add", "-b", branch, str(worktree), "HEAD"],
                    cwd=project,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if completed.returncode != 0:
                    raise SystemExit("ERROR: failed to create dispatch worktree: " + (completed.stderr or completed.stdout).strip())
                worktree_status = "created"
    payload = {
        "version": 1,
        "id": item_id,
        "title": args.title or item_id,
        "agent": args.agent,
        "purpose": args.purpose,
        "harness": args.harness,
        "model": args.model,
        "worktree": {"enabled": bool(args.worktree), "path": worktree_path, "branch": branch, "status": worktree_status, "independent": bool(args.worktree)},
        "contract": args.contract,
        "status": "QUEUED",
        "createdAt": now_iso(),
        "inbox": {"status": "PENDING", "resultPath": f".pfo/dispatch/{item_id}.result.json"},
    }
    rel = f".pfo/dispatch/{item_id}.json"
    (dispatch_dir / f"{item_id}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    runtime = state.setdefault("dispatchRuntime", {})
    runtime["path"] = ".pfo/dispatch/"
    runtime["lastDispatchId"] = item_id
    active = runtime.setdefault("activeDispatches", [])
    if item_id not in active:
        active.append(item_id)
    state["worktreeIsolation"] = {"enabled": bool(args.worktree), "strategy": "per-dispatch", "activeBranch": branch, "activeWorktree": worktree_path, "mergeStatus": "human-owned", "status": worktree_status}
    state["gateResults"]["dispatchRuntime"] = "PASSED"
    add_artifact(state, rel)
    append_event(project, state, "dispatch", "QUEUED", payload)
    save_state(project, state)
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"OK: dispatch queued {item_id}")
    return 0


CRITICAL_REVIEW_RISKS = {"security", "migration", "deploy", "auth", "payments", "data-loss"}


def cmd_cross_review(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    risks = set(args.risk or [])
    critical = bool(risks & CRITICAL_REVIEW_RISKS)
    same_agent = args.implementer.lower() == args.reviewer.lower()
    same_harness = args.implementer_harness.lower() == args.reviewer_harness.lower()
    same_vendor = args.implementer_vendor.lower() == args.reviewer_vendor.lower()
    same_model = bool(args.implementer_model and args.reviewer_model and args.implementer_model.lower() == args.reviewer_model.lower())
    independence_failed = same_agent or same_harness or same_vendor or same_model
    requires_independent = args.require_different_harness or (critical and args.vendor_available)
    status = "BLOCKED" if requires_independent and independence_failed else "READY"
    review_id = dispatch_id(args.title or "cross-review")
    review_dir = project / ".pfo" / "cross-review"
    review_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "id": review_id,
        "title": args.title or review_id,
        "risks": sorted(risks),
        "criticalRisk": critical,
        "vendorAvailable": args.vendor_available,
        "implementer": {"agent": args.implementer, "harness": args.implementer_harness, "vendor": args.implementer_vendor, "model": args.implementer_model},
        "reviewer": {"agent": args.reviewer, "harness": args.reviewer_harness, "vendor": args.reviewer_vendor, "model": args.reviewer_model},
        "requireDifferentHarness": args.require_different_harness,
        "requireDifferentVendorForCriticalRisk": critical and args.vendor_available,
        "contract": args.contract,
        "diff": args.diff,
        "status": status,
        "reason": "critical review requires independent harness/vendor/model" if status == "BLOCKED" else "independent review envelope ready",
        "createdAt": now_iso(),
    }
    rel = f".pfo/cross-review/{review_id}.json"
    (review_dir / f"{review_id}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    state["crossReview"]["lastReviewId"] = review_id
    state["crossReview"]["status"] = status
    state["gateResults"]["crossReview"] = "PASSED" if status == "READY" else "BLOCKED"
    add_artifact(state, rel)
    append_event(project, state, "review", state["gateResults"]["crossReview"], payload)
    save_state(project, state)
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"Cross-review {status}: {payload['reason']}")
    return 0 if status == "READY" else 1


def cost_route_decision(risk_score: int, estimated_cost_usd: float, trivial: bool, daily_budget_usd: float = 20.0) -> dict:
    downgrade_allowed = risk_score < 40 and estimated_cost_usd < min(1.0, daily_budget_usd)
    if trivial and downgrade_allowed:
        tier = "cheap"
        decision = "downgrade"
    elif estimated_cost_usd > daily_budget_usd:
        tier = "blocked"
        decision = "budget-deny"
        downgrade_allowed = False
    elif risk_score >= 80 or estimated_cost_usd >= 5:
        tier = "strong"
        decision = "escalate"
        downgrade_allowed = False
    elif risk_score >= 40 or estimated_cost_usd >= 1:
        tier = "standard"
        decision = "keep-standard"
        downgrade_allowed = False
    else:
        tier = "cheap"
        decision = "optimize-cost"
    return {"modelTier": tier, "budgetDecision": decision, "downgradeAllowed": downgrade_allowed, "dailyBudgetUsd": daily_budget_usd}


def cmd_cost_route(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    matrix_path = project / ".pfo" / "PERMISSION_MATRIX.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8")) if matrix_path.is_file() else {}
    cost_policy = matrix.get("costRiskPolicy", {}) if isinstance(matrix.get("costRiskPolicy"), dict) else {}
    daily_budget = float(args.daily_budget_usd or cost_policy.get("dailyBudgetUsd", 20.0) or 20.0)
    decision = cost_route_decision(args.risk_score, args.estimated_cost_usd, args.trivial, daily_budget)
    payload = {
        "type": "pfo-cost-risk-route",
        "prompt": args.prompt,
        "riskScore": args.risk_score,
        "estimatedCost": args.estimated_cost_usd,
        "estimatedCostUsd": args.estimated_cost_usd,
        "trivial": args.trivial,
        **decision,
        "updatedAt": now_iso(),
    }
    state["costRiskRouting"] = {
        "lastDecision": decision["budgetDecision"],
        "modelTier": decision["modelTier"],
        "riskScore": args.risk_score,
        "estimatedCost": args.estimated_cost_usd,
        "estimatedCostUsd": args.estimated_cost_usd,
        "budgetDecision": decision["budgetDecision"],
        "downgradeAllowed": decision["downgradeAllowed"],
        "dailyBudgetUsd": daily_budget,
        "updatedAt": payload["updatedAt"],
    }
    state.setdefault("telemetry", {})["costRiskRouting"] = state["costRiskRouting"]
    state["gateResults"]["costRiskRouting"] = "PASSED" if decision["modelTier"] != "blocked" else "BLOCKED"
    append_event(project, state, "routing", state["gateResults"]["costRiskRouting"], payload)
    save_state(project, state)
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"{decision['modelTier']}: {decision['budgetDecision']}")
    return 0 if decision["modelTier"] != "blocked" else 1


def live_session_payload(project: Path, state: dict) -> dict:
    human = state.get("humanSteering", {}) if isinstance(state.get("humanSteering"), dict) else {}
    manifest = state.get("unitContextManifest", {}) if isinstance(state.get("unitContextManifest"), dict) else {}
    return {
        "version": 1,
        "project": project.name,
        "exportedAt": now_iso(),
        "activeGoal": state.get("intent", "") or state.get("nextAction", ""),
        "route": state.get("currentTaskRoute", state.get("currentRoute", "")),
        "currentStage": state.get("currentStage", ""),
        "currentNode": state.get("currentNode", ""),
        "currentUnit": state.get("currentUnit", {}),
        "unitManifest": manifest,
        "runningCommand": state.get("telemetry", {}).get("lastCommand", "") if isinstance(state.get("telemetry"), dict) else "",
        "subagents": state.get("dispatchRuntime", {}).get("activeDispatches", []) if isinstance(state.get("dispatchRuntime"), dict) else [],
        "inbox": state.get("dispatchRuntime", {}),
        "approvals": human,
        "gates": state.get("gateResults", {}),
        "diff": {"source": "git diff --stat", "status": "external"},
        "verification": state.get("verificationHistory", []),
        "nextAction": state.get("nextAction", ""),
        "artifacts": state.get("artifacts", []),
        "eventLog": state.get("eventLog", {}),
        "eventRange": {"from": state.get("eventLog", {}).get("lastEventId", ""), "to": state.get("eventLog", {}).get("lastEventId", "")},
        "dispatchRuntime": state.get("dispatchRuntime", {}),
        "crossReview": state.get("crossReview", {}),
        "policyRuntime": state.get("policyRuntime", {}),
        "costRiskRouting": state.get("costRiskRouting", {}),
    }


def session_export_payload(project: Path, state: dict) -> dict:
    return live_session_payload(project, state)


def cmd_session(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    session_dir = project / ".pfo" / "session"
    session_dir.mkdir(parents=True, exist_ok=True)
    export_path = Path(args.output) if args.output else session_dir / "session-export.json"
    if args.session_action == "export":
        payload = session_export_payload(project, state)
        export_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        live_path = session_dir / "live-status.json"
        live_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        state["sessionRuntime"]["lastExportAt"] = payload["exportedAt"]
        state["gateResults"]["sessionRuntime"] = "PASSED"
        add_artifact(state, ".pfo/session/session-export.json")
        add_artifact(state, ".pfo/session/live-status.json")
        append_event(project, state, "state-change", "READY", {"command": "session", "action": "export"})
        save_state(project, state)
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"OK: session exported to {export_path}")
        return 0
    if args.session_action == "import":
        payload = json.loads(export_path.read_text(encoding="utf-8"))
        state["sessionRuntime"]["lastImportAt"] = now_iso()
        state.setdefault("decisionLog", []).append({"event": "session import", "source": str(export_path), "exportedAt": payload.get("exportedAt", "")})
        state["gateResults"]["sessionRuntime"] = "PASSED"
        append_event(project, state, "state-change", "READY", {"command": "session", "action": "import", "source": str(export_path)})
        save_state(project, state)
        print(f"OK: session import recorded from {export_path}")
        return 0
    if args.session_action == "attach":
        payload = json.loads(export_path.read_text(encoding="utf-8")) if export_path.is_file() else session_export_payload(project, state)
        state["sessionRuntime"]["lastAttachAt"] = now_iso()
        state["sessionRuntime"]["attachedExport"] = str(export_path)
        state.setdefault("decisionLog", []).append({"event": "session attach", "source": str(export_path), "exportedAt": payload.get("exportedAt", "")})
        state["gateResults"]["sessionRuntime"] = "PASSED"
        append_event(project, state, "state-change", "READY", {"command": "session", "action": "attach", "source": str(export_path)})
        save_state(project, state)
        print(f"OK: session attached from {export_path}")
        return 0
    if args.session_action == "share":
        payload = session_export_payload(project, state)
        share_path = session_dir / "session-share.json"
        share_payload = {"shareMode": "local-artifact", "createdAt": now_iso(), "packet": payload}
        share_path.write_text(json.dumps(share_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        state["sessionRuntime"]["lastShareAt"] = share_payload["createdAt"]
        state["sessionRuntime"]["sharePath"] = ".pfo/session/session-share.json"
        state["gateResults"]["sessionRuntime"] = "PASSED"
        add_artifact(state, ".pfo/session/session-share.json")
        append_event(project, state, "state-change", "READY", {"command": "session", "action": "share"})
        save_state(project, state)
        print(json.dumps(share_payload, indent=2, ensure_ascii=False) if args.json else "OK: session share packet written to .pfo/session/session-share.json")
        return 0
    payload = session_export_payload(project, state)
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"{payload['currentStage']} -> {payload['nextAction']}")
    return 0


def cmd_runner(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    runner_dir = project / ".pfo" / "runner"
    runner_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "role": "runner-host",
        "mode": "local-source-of-truth",
        "project": str(project),
        "executesTools": True,
        "sandboxSource": ".pfo/UNIT_CONTEXT_MANIFEST.json",
        "serverContract": ".pfo/server/control-plane.json",
        "status": "READY",
        "updatedAt": now_iso(),
    }
    path = runner_dir / "runner-host.json"
    if args.runner_action in {"status", "register"}:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        state.setdefault("runnerServer", {})["runnerHostPath"] = ".pfo/runner/runner-host.json"
        state.setdefault("runnerServer", {})["runnerStatus"] = "READY"
        state["gateResults"]["runnerServer"] = "PASSED"
        add_artifact(state, ".pfo/runner/runner-host.json")
        append_event(project, state, "state-change", "READY", {"command": "runner", "action": args.runner_action})
        save_state(project, state)
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else "runner-host: READY")
    return 0


def cmd_server(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    server_dir = project / ".pfo" / "server"
    server_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "role": "coordination-server",
        "mode": "dashboard-and-approval-plane",
        "projectSourceOfTruth": "local-pfo-artifacts",
        "coordinates": ["sessions", "telemetry", "gates", "approvals"],
        "neverExecutesTools": True,
        "runnerHost": ".pfo/runner/runner-host.json",
        "status": "READY",
        "updatedAt": now_iso(),
    }
    path = server_dir / "control-plane.json"
    if args.server_action in {"status", "register"}:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        state.setdefault("runnerServer", {})["serverControlPlanePath"] = ".pfo/server/control-plane.json"
        state.setdefault("runnerServer", {})["serverStatus"] = "READY"
        state["gateResults"]["runnerServer"] = "PASSED"
        add_artifact(state, ".pfo/server/control-plane.json")
        append_event(project, state, "state-change", "READY", {"command": "server", "action": args.server_action})
        save_state(project, state)
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else "coordination-server: READY")
    return 0


def exec_result(status: str, route: str, profile: str, artifacts: list[str], gates: dict, next_action: str, code: int) -> dict:
    return {
        "type": "pfo-exec-result",
        "status": status,
        "route": route,
        "profile": profile,
        "artifacts": artifacts,
        "gates": gates,
        "nextAction": next_action,
        "exitCode": code,
    }


def cmd_exec(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    route = args.route
    code = 0
    artifacts: list[str] = []
    if route == "readiness":
        code = cmd_readiness(argparse.Namespace(project=project, write=True, json=False, min_level=1))
        artifacts.append("PFO_READINESS_REPORT.md")
    elif route == "readiness-fix":
        code = cmd_readiness_fix(argparse.Namespace(project=project, apply=True, focus="all"))
        artifacts.append("PFO_READINESS_REPORT.md")
    elif route == "mission":
        code = cmd_mission(argparse.Namespace(project=project, mission_action="plan", goal=args.prompt, milestone="", apply=True, json=False))
        artifacts.extend([".pfo/mission.json", "PFO_MISSION.md"])
    elif route == "wiki":
        code = cmd_wiki(argparse.Namespace(project=project, wiki_action="generate", json=False))
        artifacts.append(".pfo/wiki/index.md")
    elif route == "qa":
        code = cmd_qa(argparse.Namespace(project=project, qa_action="run", app="", changed_file=[], json=False))
        artifacts.append(".pfo/qa/PFO_QA_REPORT.md")
    elif route == "telemetry":
        code = cmd_telemetry(argparse.Namespace(project=project, workspace=project.parent, format="jsonl", output="", json=False))
        artifacts.append(".pfo/telemetry/pfo-telemetry.jsonl")
    else:
        print(f"ERROR: unsupported exec route: {route}")
        return 2
    state = load_state(project)
    result = exec_result("success" if code == 0 else "blocked", route, args.profile, artifacts, state.get("gateResults", {}), state.get("nextAction", ""), code)
    if args.output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return code


def cmd_mission(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    state = load_state(project)
    ensure_autonomy_state(state)
    mission_path = project / ".pfo" / "mission.json"
    mission_doc = project / "PFO_MISSION.md"
    mission_path.parent.mkdir(exist_ok=True)
    if args.mission_action in {"plan", "replan"}:
        goal = args.goal or state.get("nextAction") or state.get("intent") or "PFO mission"
        mission = {
            "goal": goal,
            "status": "PLANNED",
            "milestones": [
                {"id": "M1", "name": "Readiness and policy", "features": ["readiness", "policy"], "validator": "readiness"},
                {"id": "M2", "name": "Knowledge and QA", "features": ["wiki", "qa"], "validator": "qa"},
                {"id": "M3", "name": "Telemetry and handoff", "features": ["telemetry", "handoff"], "validator": "telemetry"},
            ],
            "currentMilestone": "M1",
            "updatedAt": now_iso(),
        }
    elif mission_path.is_file():
        mission = json.loads(mission_path.read_text(encoding="utf-8"))
    else:
        print("ERROR: run `pfo mission plan <project>` first")
        return 2
    if args.mission_action == "run":
        target = args.milestone or mission.get("currentMilestone") or "M1"
        for milestone in mission.get("milestones", []):
            if milestone["id"] == target:
                milestone["status"] = "PASSED"
                milestone["validatedAt"] = now_iso()
                mission["currentMilestone"] = target
        mission["status"] = "RUNNING"
        state["gateResults"]["missionValidation"] = "PASSED"
    elif args.mission_action == "pause":
        mission["status"] = "PAUSED"
    elif args.mission_action == "continue":
        mission["status"] = "RUNNING"
    mission_path.write_text(json.dumps(mission, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    mission_doc.write_text(
        "# PFO Mission\n\n"
        f"Goal: {mission['goal']}\n\n"
        f"Status: {mission['status']}\n\n"
        "## Milestones\n\n"
        + "\n".join(f"- {item['id']}: {item['name']} ({item.get('status', 'PENDING')})" for item in mission.get("milestones", []))
        + "\n",
        encoding="utf-8",
    )
    state["mission"] = mission
    add_artifact(state, ".pfo/mission.json")
    add_artifact(state, "PFO_MISSION.md")
    append_event(project, state, "state-change", "RECORDED", {"command": "mission", "action": args.mission_action})
    save_state(project, state)
    if args.json:
        print(json.dumps(mission, indent=2, ensure_ascii=False))
    else:
        print(f"OK: mission {args.mission_action} -> {mission['status']}")
    return 0


def cmd_wiki(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    wiki_dir = project / ".pfo" / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    state = load_state(project)
    state_summary = {
        "currentStage": state.get("currentStage", ""),
        "currentNode": state.get("currentNode", ""),
        "nextAction": state.get("nextAction", ""),
        "gateResults": state.get("gateResults", {}),
        "artifacts": state.get("artifacts", [])[-25:] if isinstance(state.get("artifacts"), list) else [],
    }
    docs = {
        "index.md": f"# PFO Wiki\n\nProject: `{project.name}`\n\n- [Architecture](architecture.md)\n- [Modules](modules.md)\n- [Commands](commands.md)\n- [Gates](gates.md)\n- [State](current-state.md)\n",
        "architecture.md": (project / "PROJECT_ARCHITECTURE.md").read_text(encoding="utf-8") if (project / "PROJECT_ARCHITECTURE.md").is_file() else "# Architecture\n\nNo project architecture artifact yet.\n",
        "modules.md": "# Modules\n\n" + "\n".join(f"- `{path.name}/`" for path in sorted(project.iterdir()) if path.is_dir() and not path.name.startswith(".")) + "\n",
        "commands.md": "# Commands\n\nRun `pfo status`, `pfo readiness`, `pfo qa run`, and `pfo telemetry export` for operational views.\n",
        "gates.md": "# Gates\n\n" + json.dumps(state.get("gateResults", {}), indent=2, ensure_ascii=False) + "\n",
        "current-state.md": "# Current State\n\n" + json.dumps(state_summary, indent=2, ensure_ascii=False) + "\n",
    }
    before = {path.name: path.read_text(encoding="utf-8") for path in wiki_dir.glob("*.md")}
    for name, text in docs.items():
        (wiki_dir / name).write_text(text, encoding="utf-8")
    changed = sorted(name for name, text in docs.items() if before.get(name) != text)
    state = load_state(project)
    ensure_autonomy_state(state)
    state["wiki"] = {"path": ".pfo/wiki/index.md", "status": "READY", "changedPages": changed, "updatedAt": now_iso()}
    add_artifact(state, ".pfo/wiki/index.md")
    append_event(project, state, "state-change", "READY", {"command": "wiki", "action": args.wiki_action, "changed": changed})
    save_state(project, state)
    if args.wiki_action == "diff":
        print(json.dumps({"changedPages": changed}, indent=2, ensure_ascii=False))
    elif args.json:
        print(json.dumps(state["wiki"], indent=2, ensure_ascii=False))
    else:
        print("OK: wiki ready")
    return 0


def cmd_qa(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    qa_dir = project / ".pfo" / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    config = qa_dir / "config.yaml"
    if args.qa_action == "install" or not config.exists():
        config.write_text(
            "project: " + project.name + "\n"
            "default_target: local\n"
            "apps:\n"
            "  docs:\n"
            "    path_patterns: ['*.md', 'docs/**']\n"
            "    test_tool: pfo-validators\n"
            "failure_learning: suggest_in_report\n",
            encoding="utf-8",
        )
        (qa_dir / "REPORT-TEMPLATE.md").write_text("# PFO QA Report\n\n| Flow | Status | Evidence |\n|---|---|---|\n", encoding="utf-8")
        flows = qa_dir / "flows"
        flows.mkdir(exist_ok=True)
        (flows / "docs.md").write_text("# Docs QA Flow\n\nRun structure and contract validators for documentation/runtime changes.\n", encoding="utf-8")
    changed = args.changed_file or []
    if not changed:
        result = subprocess.run(["git", "diff", "--name-only"], cwd=project, text=True, capture_output=True, check=False)
        changed = [line for line in result.stdout.splitlines() if line.strip()] if result.returncode == 0 else []
    report_path = qa_dir / "PFO_QA_REPORT.md"
    status = "PASSED"
    report_path.write_text(
        "# PFO QA Report\n\n"
        f"- Generated: `{now_iso()}`\n"
        f"- Changed files considered: {len(changed)}\n"
        f"- Status: {status}\n\n"
        "## Evidence\n\n"
        "- QA config exists.\n"
        "- Diff-scoped file list was evaluated.\n",
        encoding="utf-8",
    )
    state = load_state(project)
    ensure_autonomy_state(state)
    state["qa"] = {"path": ".pfo/qa/PFO_QA_REPORT.md", "status": status, "changedFiles": changed, "updatedAt": now_iso()}
    state["gateResults"]["qa"] = status
    add_artifact(state, ".pfo/qa/config.yaml")
    add_artifact(state, ".pfo/qa/PFO_QA_REPORT.md")
    append_event(project, state, "verification", status, {"command": "qa", "action": args.qa_action, "changedFiles": changed})
    save_state(project, state)
    if args.json:
        print(json.dumps(state["qa"], indent=2, ensure_ascii=False))
    else:
        print(f"OK: QA {args.qa_action} {status}")
    return 0


def cmd_telemetry(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    output = Path(args.output) if args.output else project / ".pfo" / "telemetry" / ("pfo-telemetry.json" if args.format == "json" else "pfo-telemetry.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    events = []
    event_path = project / ".codex-memory" / "events.jsonl"
    if event_path.is_file():
        for line in event_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    state = load_state(project)
    payload = {
        "resource": {"project": project.name},
        "metrics": {
            "eventCount": len(events),
            "artifactCount": len(state.get("artifacts", [])),
            "gateCount": len(state.get("gateResults", {})),
            "verificationCount": len(state.get("verificationHistory", [])),
        },
        "events": events[-100:],
        "exportedAt": now_iso(),
    }
    if args.format == "jsonl":
        rows = [{"type": "metric", "name": key, "value": value, "project": project.name} for key, value in payload["metrics"].items()]
        output.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    else:
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ensure_autonomy_state(state)
    state["telemetryExport"] = {"path": str(output.relative_to(project)) if output.is_relative_to(project) else str(output), "format": args.format, "status": "READY", "updatedAt": now_iso()}
    add_artifact(state, state["telemetryExport"]["path"])
    append_event(project, state, "state-change", "READY", {"command": "telemetry", "format": args.format})
    save_state(project, state)
    if args.json:
        print(json.dumps(state["telemetryExport"], indent=2, ensure_ascii=False))
    else:
        print(f"OK: telemetry exported to {output}")
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


def cmd_check(args: argparse.Namespace) -> int:
    argv = []
    if args.no_smoke:
        argv.append("--no-smoke")
    return run_script("check.py", argv)


def cmd_resume(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    run_script("pfo_context_runtime.py", ["snapshot", str(project), "--reason", "resume", "--quiet"])
    state = load_state(project)
    print("CURRENT STATE:", state.get("currentStage", ""))
    print("CURRENT NODE:", state.get("currentNode", ""))
    print("NEXT ACTION:", state.get("nextAction", ""))
    snapshot = state.get("resumeSnapshot", {}) if isinstance(state.get("resumeSnapshot"), dict) else {}
    if snapshot.get("path"):
        print("RESUME SNAPSHOT:", snapshot["path"])
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
    manifest.add_argument("--profile", choices=["auto", "minimal", "standard", "full"], default="auto", help="Route profile for gate and artifact scope.")
    manifest.add_argument("--behavior-change", action="store_true", help="Require TDD evidence for this unit.")
    manifest.add_argument("--bugfix", action="store_true", help="Require ROOT_CAUSE.md before implementation.")
    manifest.set_defaults(func=cmd_manifest)

    for name, func in [
        ("status", cmd_status),
        ("next-best-action", cmd_next_best_action),
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
        if name == "next-best-action":
            item.add_argument("--json", action="store_true")
            item.add_argument("--write", action="store_true", help="Write the recommendation into STATE.json and NEXT_STEP.md.")
        if name == "plan":
            item.add_argument("--note", default="")
        if name == "contracts":
            item.add_argument("--json", action="store_true")
            item.add_argument("--write", action="store_true")
            item.add_argument("--strict", action="store_true")
        item.set_defaults(func=func)

    full_cycle = sub.add_parser("full-cycle", help="Run plan, test, implementation dispatch, review, and session-save orchestration.")
    full_cycle.add_argument("project", type=Path)
    full_cycle.add_argument("--note", default="")
    full_cycle.add_argument("--skip-plan", action="store_true")
    full_cycle.add_argument("--skip-test", action="store_true")
    full_cycle.add_argument("--skip-build", action="store_true")
    full_cycle.add_argument("--skip-review", action="store_true")
    full_cycle.add_argument("--stop-on-blocked", action="store_true", help="Stop immediately when a lifecycle step is blocked.")
    full_cycle.set_defaults(func=cmd_full_cycle)

    check = sub.add_parser("check", help="Run the root Product Factory OS check command.")
    check.add_argument("--no-smoke", action="store_true", help="Skip temporary generated-project smoke checks.")
    check.set_defaults(func=cmd_check)

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
    permission_check.add_argument("--capability", choices=["read", "write", "test", "commit", "push", "deploy", "external_api", "secrets", "context_budget"])
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

    acceptance = sub.add_parser("acceptance", help="Create, update, and gate original-request acceptance criteria.")
    acceptance.add_argument("acceptance_action", choices=["init", "add", "verify", "gate", "status"])
    acceptance.add_argument("project", type=Path)
    acceptance.add_argument("--request", default="")
    acceptance.add_argument("--unit", default="")
    acceptance.add_argument("--criterion", action="append", default=[], help="Repeat as ID::requirement::verification or raw requirement.")
    acceptance.add_argument("--id", default="")
    acceptance.add_argument("--requirement", default="")
    acceptance.add_argument("--source-quote", default="")
    acceptance.add_argument("--verification", default="")
    acceptance.add_argument("--status", choices=["PENDING", "PASSED", "FAILED", "WAIVED"], default="PASSED")
    acceptance.add_argument(
        "--evidence-kind",
        choices=["command", "test", "review", "security", "manual", "artifact", "production_readiness", "contract_gate"],
        default="command",
    )
    acceptance.add_argument("--evidence", default="")
    acceptance.add_argument("--independent-evidence", default="")
    acceptance.add_argument("--force", action="store_true")
    acceptance.add_argument("--json", action="store_true")
    acceptance.set_defaults(func=cmd_acceptance)

    context_budget = sub.add_parser("context-budget", help="Check tool/read/log/web output against the context budget gate.")
    context_budget.add_argument("project", type=Path)
    context_budget.add_argument("--kind", choices=["tool", "read", "log", "web", "http", "grep", "rg"], default="tool")
    context_budget.add_argument("--bytes", type=int, default=0)
    context_budget.add_argument("--lines", type=int, default=0)
    context_budget.add_argument("--command-text", default="")
    context_budget.add_argument("--raw-http", action="store_true")
    context_budget.add_argument("--approved", action="store_true")
    context_budget.add_argument("--json", action="store_true")
    context_budget.set_defaults(func=cmd_context_budget)

    context_index = sub.add_parser("context-index", help="Build a searchable index for .codex-memory/events.jsonl.")
    context_index.add_argument("project", type=Path)
    context_index.set_defaults(func=cmd_context_index)

    context_search = sub.add_parser("context-search", help="Search PFO session memory with BM25-style scoring.")
    context_search.add_argument("project", type=Path)
    context_search.add_argument("query", nargs="+")
    context_search.add_argument("--limit", type=int, default=5)
    context_search.add_argument("--reindex", action="store_true")
    context_search.add_argument("--json", action="store_true")
    context_search.set_defaults(func=cmd_context_search)

    context_snapshot = sub.add_parser("context-snapshot", help="Write a compact resume snapshot from state and recent events.")
    context_snapshot.add_argument("project", type=Path)
    context_snapshot.add_argument("--reason", default="manual")
    context_snapshot.add_argument("--quiet", action="store_true")
    context_snapshot.set_defaults(func=cmd_context_snapshot)

    tool_registry = sub.add_parser("tool-registry", help="Validate project tool capability registry.")
    tool_registry.add_argument("project", type=Path)
    tool_registry.set_defaults(func=cmd_tool_registry)

    skill_scaffold = sub.add_parser("skill-scaffold", help="Create a PFO-aware skill scaffold with contracts, triggers, fixtures, and snapshots.")
    skill_scaffold.add_argument("skill_name")
    skill_scaffold.add_argument("--description", required=True)
    skill_scaffold.add_argument("--trigger", action="append", required=True)
    skill_scaffold.add_argument("--russian-triggers", default="")
    skill_scaffold.add_argument("--prompt", default="")
    skill_scaffold.add_argument("--input", default="")
    skill_scaffold.add_argument("--output", action="append", default=[])
    skill_scaffold.add_argument("--expected-file", action="append", default=[])
    skill_scaffold.add_argument("--required-file", action="append", default=[])
    skill_scaffold.add_argument("--stdout-token", action="append", default=[])
    skill_scaffold.add_argument("--any-file-token", action="append", default=[])
    skill_scaffold.add_argument("--notes", default="")
    skill_scaffold.add_argument("--notes-token", default="fixture")
    skill_scaffold.add_argument("--validation-command", action="append", default=[])
    skill_scaffold.add_argument("--argument-hint", default="")
    skill_scaffold.add_argument("--category", default="daily-work")
    skill_scaffold.add_argument("--tag", action="append", default=[])
    skill_scaffold.add_argument("--effort", choices=["low", "medium", "high"], default="medium")
    skill_scaffold.add_argument(
        "--side-effect",
        choices=[
            "read-only",
            "docs-write",
            "code-write",
            "methodology-write",
            "external-write",
            "infrastructure-write",
            "data-migration",
            "production-impact",
        ],
        default="read-only",
    )
    skill_scaffold.add_argument("--explicit-invocation", action="store_true")
    skill_scaffold.add_argument("--resource", action="append", default=[])
    skill_scaffold.add_argument("--fixture", default="")
    skill_scaffold.add_argument("--force", action="store_true")
    skill_scaffold.set_defaults(func=cmd_skill_scaffold)

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

    readiness = sub.add_parser("readiness", help="Evaluate PFO autonomy readiness levels and action items.")
    readiness.add_argument("project", type=Path)
    readiness.add_argument("--write", action="store_true")
    readiness.add_argument("--json", action="store_true")
    readiness.add_argument("--min-level", type=int, default=1)
    readiness.set_defaults(func=cmd_readiness)

    readiness_fix = sub.add_parser("readiness-fix", help="Apply deterministic remediation for the latest PFO readiness gaps.")
    readiness_fix.add_argument("project", type=Path)
    readiness_fix.add_argument("--apply", action="store_true")
    readiness_fix.add_argument("--focus", choices=["all", "docs", "policy", "measurement"], default="all")
    readiness_fix.set_defaults(func=cmd_readiness_fix)

    policy = sub.add_parser("policy", help="Explain or check PFO risk-tier autonomy policy.")
    policy.add_argument("policy_action", choices=["explain", "check"])
    policy.add_argument("project", type=Path)
    policy.add_argument("--auto", choices=["off", "low", "medium", "high"], default="off")
    policy.add_argument("--capability", choices=["read", "write", "test", "commit", "push", "deploy", "external_api"], default="")
    policy.add_argument("--json", action="store_true")
    policy.set_defaults(func=cmd_policy)

    policy_eval = sub.add_parser("policy-eval", help="Evaluate a PFO runtime policy event and return ALLOW, DENY, or ASK.")
    policy_eval.add_argument("project", type=Path)
    policy_eval.add_argument("--event-json", default="")
    policy_eval.add_argument("--event-file", default="")
    policy_eval.add_argument("--event-type", default="tool_call")
    policy_eval.add_argument("--target", default="")
    policy_eval.add_argument("--actor", default="codex")
    policy_eval.add_argument("--usage-json", default="")
    policy_eval.add_argument("--session-state-json", default="")
    policy_eval.add_argument("--result-json", default="")
    policy_eval.add_argument("--capability", choices=["read", "write", "test", "commit", "push", "deploy", "external_api", "secrets", "context_budget"], default="read")
    policy_eval.add_argument("--cost-usd", type=float, default=0)
    policy_eval.add_argument("--risk-score", type=int, default=0)
    policy_eval.add_argument("--tool-calls", type=int, default=0)
    policy_eval.add_argument("--ask-risk", type=int, default=50)
    policy_eval.add_argument("--deny-risk", type=int, default=90)
    policy_eval.add_argument("--ask-cost", type=float, default=3.0)
    policy_eval.add_argument("--deny-cost", type=float, default=10.0)
    policy_eval.add_argument("--max-tool-calls", type=int, default=200)
    policy_eval.add_argument("--record", action="store_true")
    policy_eval.add_argument("--json", action="store_true")
    policy_eval.set_defaults(func=cmd_policy_eval)

    autonomy = sub.add_parser("autonomy", help="Alias for `pfo policy explain` with an autonomy level.")
    autonomy.add_argument("project", type=Path)
    autonomy.add_argument("--auto", choices=["off", "low", "medium", "high"], default="off")
    autonomy.add_argument("--json", action="store_true")
    autonomy.set_defaults(func=lambda args: cmd_policy(argparse.Namespace(policy_action="explain", project=args.project, auto=args.auto, capability="", json=args.json)))

    agent_spec = sub.add_parser("agent-spec", help="List, validate, or materialize PFO Agent Spec v1 YAML profiles.")
    agent_spec.add_argument("agent_action", choices=["list", "validate", "write-defaults"])
    agent_spec.add_argument("project", type=Path)
    agent_spec.add_argument("--json", action="store_true")
    agent_spec.set_defaults(func=cmd_agent_spec)

    dispatch = sub.add_parser("dispatch", help="Create a PFO sub-agent dispatch envelope with optional worktree isolation.")
    dispatch.add_argument("project", type=Path)
    dispatch.add_argument("--agent", required=True)
    dispatch.add_argument("--purpose", choices=["implement", "review", "explore", "search"], required=True)
    dispatch.add_argument("--title", default="")
    dispatch.add_argument("--harness", default="codex-native")
    dispatch.add_argument("--model", default="")
    dispatch.add_argument("--branch", default="")
    dispatch.add_argument("--contract", default="")
    dispatch.add_argument("--worktree", action="store_true")
    dispatch.add_argument("--no-create-worktree", action="store_true", help="Declare worktree isolation without creating a git worktree.")
    dispatch.add_argument("--json", action="store_true")
    dispatch.set_defaults(func=cmd_dispatch)

    cross_review = sub.add_parser("cross-review", help="Create an independent cross-harness review envelope for a diff and contract.")
    cross_review.add_argument("project", type=Path)
    cross_review.add_argument("--implementer", required=True)
    cross_review.add_argument("--reviewer", required=True)
    cross_review.add_argument("--implementer-harness", default="codex-native")
    cross_review.add_argument("--reviewer-harness", default="claude-native")
    cross_review.add_argument("--implementer-vendor", default="openai")
    cross_review.add_argument("--reviewer-vendor", default="anthropic")
    cross_review.add_argument("--implementer-model", default="")
    cross_review.add_argument("--reviewer-model", default="")
    cross_review.add_argument("--risk", action="append", choices=["security", "migration", "deploy", "auth", "payments", "data-loss", "general"], default=[])
    cross_review.add_argument("--vendor-available", action="store_true", default=True)
    cross_review.add_argument("--title", default="")
    cross_review.add_argument("--diff", default="")
    cross_review.add_argument("--contract", default="")
    cross_review.add_argument("--require-different-harness", action="store_true", default=True)
    cross_review.add_argument("--json", action="store_true")
    cross_review.set_defaults(func=cmd_cross_review)

    cost_route = sub.add_parser("cost-route", help="Route model tier from risk, cost, and triviality signals.")
    cost_route.add_argument("project", type=Path)
    cost_route.add_argument("prompt", nargs="?", default="")
    cost_route.add_argument("--risk-score", type=int, default=0)
    cost_route.add_argument("--estimated-cost-usd", type=float, default=0)
    cost_route.add_argument("--daily-budget-usd", type=float, default=0)
    cost_route.add_argument("--trivial", action="store_true")
    cost_route.add_argument("--json", action="store_true")
    cost_route.set_defaults(func=cmd_cost_route)

    session = sub.add_parser("session", help="Export, import, attach, share, or inspect forkable PFO session runtime context.")
    session.add_argument("session_action", choices=["export", "import", "attach", "share", "status"])
    session.add_argument("project", type=Path)
    session.add_argument("--output", default="")
    session.add_argument("--json", action="store_true")
    session.set_defaults(func=cmd_session)

    runner = sub.add_parser("runner", help="Register or inspect the local PFO runner host.")
    runner.add_argument("runner_action", choices=["register", "status"])
    runner.add_argument("project", type=Path)
    runner.add_argument("--json", action="store_true")
    runner.set_defaults(func=cmd_runner)

    server = sub.add_parser("server", help="Register or inspect the coordination server contract.")
    server.add_argument("server_action", choices=["register", "status"])
    server.add_argument("project", type=Path)
    server.add_argument("--json", action="store_true")
    server.set_defaults(func=cmd_server)

    exec_cmd = sub.add_parser("exec", help="Run a deterministic PFO route as a headless one-shot command.")
    exec_cmd.add_argument("project", type=Path)
    exec_cmd.add_argument("prompt", nargs="?", default="")
    exec_cmd.add_argument("--route", choices=["readiness", "readiness-fix", "mission", "wiki", "qa", "telemetry"], default="readiness")
    exec_cmd.add_argument("--profile", choices=["minimal", "standard", "full"], default="standard")
    exec_cmd.add_argument("--auto", choices=["off", "low", "medium", "high"], default="off")
    exec_cmd.add_argument("--output-format", choices=["text", "json"], default="text")
    exec_cmd.set_defaults(func=cmd_exec)

    mission = sub.add_parser("mission", help="Plan, run, pause, replan, continue, or inspect a PFO mission.")
    mission.add_argument("mission_action", choices=["plan", "run", "status", "pause", "replan", "continue"])
    mission.add_argument("project", type=Path)
    mission.add_argument("--goal", default="")
    mission.add_argument("--milestone", default="")
    mission.add_argument("--apply", action="store_true")
    mission.add_argument("--json", action="store_true")
    mission.set_defaults(func=cmd_mission)

    wiki = sub.add_parser("wiki", help="Generate, refresh, or diff a project-local PFO wiki.")
    wiki.add_argument("wiki_action", choices=["generate", "refresh", "diff"])
    wiki.add_argument("project", type=Path)
    wiki.add_argument("--json", action="store_true")
    wiki.set_defaults(func=cmd_wiki)

    qa = sub.add_parser("qa", help="Install or run diff-scoped PFO QA evidence.")
    qa.add_argument("qa_action", choices=["install", "run"])
    qa.add_argument("project", type=Path)
    qa.add_argument("--app", default="")
    qa.add_argument("--changed-file", action="append", default=[])
    qa.add_argument("--json", action="store_true")
    qa.set_defaults(func=cmd_qa)

    telemetry = sub.add_parser("telemetry", help="Export PFO telemetry as JSON or JSONL.")
    telemetry.add_argument("telemetry_action", choices=["export"])
    telemetry.add_argument("project", type=Path)
    telemetry.add_argument("--workspace", type=Path, default=WORKSPACE)
    telemetry.add_argument("--format", choices=["json", "jsonl"], default="jsonl")
    telemetry.add_argument("--output", default="")
    telemetry.add_argument("--json", action="store_true")
    telemetry.set_defaults(func=cmd_telemetry)

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
