#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import re
import subprocess
import sys
from typing import Any

from pfo_alias_targets import missing_alias_targets

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_CONTRACTS = [
    ".pfo/PROJECT_CONTRACT.md",
    ".pfo/DATA_POLICY.md",
    ".pfo/GOLDEN_FLOWS.md",
    ".pfo/FORBIDDEN_CHANGES.md",
    ".pfo/FALLBACK_POLICY.md",
    ".pfo/SCOPE_LOCK.md",
    ".pfo/PERMISSION_MATRIX.md",
    ".pfo/PERMISSION_MATRIX.json",
    ".pfo/LEARNING_PROMOTION_GATE.md",
    ".pfo/EXECUTION_POLICY.json",
    ".pfo/VERIFICATION_CONTRACT.json",
    ".pfo/TOOL_CAPABILITY_REGISTRY.json",
]

PFO_RUNTIME_DIFF_EXACT_PATHS = {
    "AGENTS.md",
    "BRANCH_FINISH.md",
    "CODEX.md",
    "HANDOFF.md",
    "NEXT_STEP.md",
    "PFO_CONTRACT_GATE.json",
    "PFO_EXISTING_PROJECT_ANALYSIS.json",
    "PFO_REPORT.md",
}

PFO_RUNTIME_DIFF_PREFIXES = (
    ".codex-memory/",
    ".pfo/",
)

TEST_PATH_MARKERS = (
    "/test/",
    "/tests/",
    "__tests__",
    ".test.",
    ".spec.",
    "/fixtures/",
    "/mocks/",
    "/examples/",
)

DOCUMENTATION_SUFFIXES = (
    ".md",
    ".txt",
    ".rst",
)

RISK_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("dependency_change", ("package.json", "lock", "requirements.txt", "pyproject.toml", "go.mod", "cargo.toml")),
    ("business_logic_change", ("service", "domain", "usecase", "handler", "route", "controller", "job", "workflow")),
    ("data_source_change", ("source", "database", "db", "sql", "supabase", "postgres", "query", "schema", "migration")),
    ("provider_integration_change", ("openai", "anthropic", "llm", "provider", "api_key", "webhook", "client")),
    ("user_facing_output_change", ("page", "component", "template", "message", "response", "copy", "ui", "frontend")),
    ("security_change", ("auth", "token", "secret", "permission", "policy", "security", "csrf", "cors")),
    ("deployment_change", ("docker", "deploy", "compose", "k8s", "terraform", "vercel", "netlify", "ci", "workflow")),
]

SECURITY_REPORT_FILENAMES = {
    "security_audit_report.md",
    "security-audit-report.md",
    "security_review.md",
    "security-review.md",
    "pfo_security_review.md",
    "pfo-security-review.md",
}

SECURITY_COVERAGE_ARTIFACTS = [
    "deep_review_input.csv",
    "work_ledger.jsonl",
    "repository_coverage_ledger.md",
    "candidate_ledger.jsonl",
]

SUBSTITUTION_TERMS = (
    "fake",
    "mock",
    "stub",
    "dummy",
    "hardcoded",
    "synthetic",
    "placeholder",
    "fallback",
    "заглуш",
    "фейк",
    "мок",
    "тестов",
)

TRANSPARENT_TERMS = (
    "unavailable",
    "degraded",
    "error",
    "retry",
    "queue",
    "cache",
    "fixture",
    "test",
    "explicit",
    "approved",
    "approval",
    "visible",
    "declared",
    "record",
    "documented",
    "недоступ",
    "ошиб",
    "повтор",
    "очеред",
)


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def run_git(project: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=project,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout


def changed_files(project: Path) -> list[str]:
    output = run_git(project, ["diff", "--name-only"])
    staged = run_git(project, ["diff", "--cached", "--name-only"])
    untracked = run_git(project, ["ls-files", "--others", "--exclude-standard"])
    names = {line.strip() for line in (output + "\n" + staged + "\n" + untracked).splitlines() if line.strip()}
    return sorted(names)


def is_pfo_runtime_diff_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized in PFO_RUNTIME_DIFF_EXACT_PATHS or normalized.startswith(PFO_RUNTIME_DIFF_PREFIXES)


def is_self_adopted_pfo_repo(project: Path) -> bool:
    try:
        if project.resolve() == ROOT.resolve():
            return True
    except OSError:
        pass
    return (
        (project / "scripts" / "pfo.py").is_file()
        and (project / "scripts" / "pfo_contract_gate.py").is_file()
        and (project / ".pfo" / "PROJECT_CONTRACT.md").is_file()
    )


def product_changed_files(files: list[str]) -> list[str]:
    return [path for path in files if not is_pfo_runtime_diff_path(path)]


def diff_text(project: Path, files: list[str] | None = None) -> str:
    if files == []:
        return ""
    pathspec = ["."] if files is None else files
    unstaged = run_git(project, ["diff", "--", *pathspec])
    staged = run_git(project, ["diff", "--cached", "--", *pathspec])
    return "\n".join(part for part in [unstaged, staged] if part)


def is_test_path(path: str) -> bool:
    normalized = "/" + path.lower().replace("\\", "/")
    return any(marker in normalized for marker in TEST_PATH_MARKERS)


def is_documentation_path(path: str) -> bool:
    return path.lower().replace("\\", "/").endswith(DOCUMENTATION_SUFFIXES)


def addition_lines(diff: str) -> list[tuple[str, str]]:
    current = ""
    result: list[tuple[str, str]] = []
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            continue
        if line.startswith("+") and not line.startswith("+++"):
            result.append((current, line[1:]))
    return result


def contains_substitution_term(text: str) -> bool:
    for term in SUBSTITUTION_TERMS:
        if term.isascii() and term.replace("_", "").replace("-", "").isalnum():
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", text):
                return True
        elif term in text:
            return True
    return False


def classify_risks(files: list[str], diff: str) -> list[str]:
    corpus = "\n".join(files) + "\n" + diff
    lowered = corpus.lower()
    risks = set()
    for risk, markers in RISK_RULES:
        if any(marker in lowered for marker in markers):
            risks.add(risk)
    if files and all(is_test_path(path) for path in files):
        risks.add("test_only_change")
    if files and all(is_documentation_path(path) for path in files):
        risks.add("documentation_change")
    return sorted(risks)


def parse_forbidden_terms(path: Path) -> list[str]:
    if not path.is_file():
        return []
    terms: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("- "):
            continue
        text = line[2:].strip().strip(".")
        if text and "replace this line" not in text.lower():
            terms.append(text.lower())
    return terms


def missing_contracts(project: Path) -> list[str]:
    return [rel for rel in REQUIRED_CONTRACTS if not (project / rel).is_file()]


def has_placeholder_contracts(project: Path) -> list[str]:
    placeholders: list[str] = []
    for rel in REQUIRED_CONTRACTS:
        path = project / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8").lower()
        if "replace this line" in text:
            placeholders.append(rel)
    return placeholders


def json_contract_errors(project: Path) -> list[str]:
    errors: list[str] = []
    for rel, required in {
        ".pfo/EXECUTION_POLICY.json": ["commandPolicy", "writePolicy", "networkPolicy", "approvalPolicy"],
        ".pfo/PERMISSION_MATRIX.json": ["actors", "capabilities", "rules"],
        ".pfo/VERIFICATION_CONTRACT.json": ["commands", "requiredArtifacts", "passCriteria", "failureMode"],
        ".pfo/TOOL_CAPABILITY_REGISTRY.json": ["tools", "selectionPolicy"],
    }.items():
        path = project / rel
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: invalid JSON: {exc}")
            continue
        for field in required:
            if field not in data:
                errors.append(f"{rel}: missing {field}")
        if rel.endswith("PERMISSION_MATRIX.json"):
            for capability in ["read", "write", "test", "commit", "push", "deploy", "external_api", "secrets", "context_budget"]:
                if capability not in data.get("capabilities", {}):
                    errors.append(f"{rel}: missing capability {capability}")
            if "contextRuntimePolicy" not in data:
                errors.append(f"{rel}: missing contextRuntimePolicy")
        if rel.endswith("TOOL_CAPABILITY_REGISTRY.json"):
            selection_policy = data.get("selectionPolicy")
            if not isinstance(selection_policy, dict):
                errors.append(f"{rel}: selectionPolicy must be an object")
            elif selection_policy.get("mode") != "progressive-disclosure":
                errors.append(f"{rel}: selectionPolicy.mode must be progressive-disclosure")
            tools = data.get("tools", [])
            if not isinstance(tools, list) or not tools:
                errors.append(f"{rel}: tools must be a non-empty list")
            for index, tool in enumerate(tools, start=1):
                if not isinstance(tool, dict):
                    errors.append(f"{rel}: tool {index} must be an object")
                    continue
                for field in ["id", "capabilities", "sideEffects", "authNeeded", "externalDataRisk", "fallbackMode", "approvalRequiredFor"]:
                    if field not in tool:
                        errors.append(f"{rel}: tool {index} missing {field}")
    return errors


def detect_substitution_violations(project: Path, diff: str) -> list[str]:
    violations: list[str] = []
    forbidden_terms = parse_forbidden_terms(project / ".pfo" / "FORBIDDEN_CHANGES.md")
    for path, line in addition_lines(diff):
        lowered = line.lower()
        if is_test_path(path):
            continue
        if contains_substitution_term(lowered):
            if not any(term in lowered for term in TRANSPARENT_TERMS):
                violations.append(f"{path}: added possible silent substitution: {line[:160]}")
        for term in forbidden_terms:
            if len(term) > 12 and term in lowered:
                violations.append(f"{path}: added project-forbidden behavior: {term[:120]}")
    return violations


def candidate_security_reports(project: Path, files: list[str]) -> list[Path]:
    candidates: set[Path] = set()
    for rel in files:
        normalized = rel.replace("\\", "/")
        lowered = normalized.lower()
        path = project / normalized
        name = Path(lowered).name
        if name in SECURITY_REPORT_FILENAMES:
            candidates.add(path)
        elif lowered.startswith("reports/") and "security" in lowered and lowered.endswith(".md"):
            candidates.add(path)
    for pattern in [
        "SECURITY_AUDIT_REPORT.md",
        "PFO_SECURITY_REVIEW.md",
        "reports/**/*security*.md",
    ]:
        for path in project.glob(pattern):
            if "docs/templates" not in path.as_posix() and path.is_file():
                candidates.add(path)
    return sorted(candidates)


def validate_security_report(project: Path, report: Path) -> tuple[bool, str]:
    validator = project / "scripts" / "validate_security_report.py"
    if not validator.is_file():
        return False, "scripts/validate_security_report.py is missing"
    completed = subprocess.run(
        [sys.executable, str(validator), str(report)],
        cwd=project,
        text=True,
        capture_output=True,
    )
    if completed.returncode == 0:
        return True, str(report.relative_to(project))
    detail = (completed.stdout + completed.stderr).strip().replace("\n", "; ")
    return False, f"{report.relative_to(project)} failed security report validation: {detail}"


def security_coverage_artifact_errors(files: list[str]) -> list[str]:
    errors: list[str] = []
    changed_names = {Path(path.replace("\\", "/")).name for path in files}
    for name in SECURITY_COVERAGE_ARTIFACTS:
        if name not in changed_names:
            errors.append(f"missing changed security coverage artifact: {name}")
    return errors


def security_evidence_subject_files(files: list[str]) -> list[str]:
    return [
        path
        for path in files
        if not is_pfo_runtime_diff_path(path)
        and not is_test_path(path)
        and not is_documentation_path(path)
    ]


def security_evidence_errors(project: Path, files: list[str], risks: list[str]) -> list[str]:
    if "security_change" not in risks:
        return []
    if not security_evidence_subject_files(files):
        return []
    errors = security_coverage_artifact_errors(files)
    reports = candidate_security_reports(project, files)
    if not reports:
        errors.append(
            "security_change requires Codex Security diff-scan evidence or a PFO-equivalent report validated by scripts/validate_security_report.py"
        )
        return errors

    validation_notes = [validate_security_report(project, report) for report in reports]
    if not any(ok for ok, _note in validation_notes):
        errors.extend(note for _ok, note in validation_notes)
    return errors


def evaluate(project: Path) -> dict[str, Any]:
    all_files = changed_files(project)
    runtime_files = [path for path in all_files if is_pfo_runtime_diff_path(path)]
    files = product_changed_files(all_files)
    diff = diff_text(project, files)
    missing = missing_contracts(project)
    placeholders = has_placeholder_contracts(project)
    json_errors = json_contract_errors(project)
    alias_target_errors = missing_alias_targets(project)
    self_adopted = is_self_adopted_pfo_repo(project)
    risks = classify_risks(files, diff)
    substitution_violations = detect_substitution_violations(project, diff)
    security_errors = security_evidence_errors(project, files, risks)
    execution_json_errors = [item for item in json_errors if item.startswith(".pfo/EXECUTION_POLICY.json")]
    permission_json_errors = [item for item in json_errors if item.startswith(".pfo/PERMISSION_MATRIX.json")]
    verification_json_errors = [item for item in json_errors if item.startswith(".pfo/VERIFICATION_CONTRACT.json")]
    tool_json_errors = [item for item in json_errors if item.startswith(".pfo/TOOL_CAPABILITY_REGISTRY.json")]

    blockers: list[str] = []
    warnings: list[str] = []
    if missing:
        blockers.extend([f"missing contract: {item}" for item in missing])
    if placeholders:
        if self_adopted:
            blockers.extend([f"self-adopted PFO repo cannot use template contract content: {item}" for item in placeholders])
        else:
            warnings.extend([f"template contract content: {item}" for item in placeholders])
    blockers.extend(json_errors)
    blockers.extend(alias_target_errors)
    blockers.extend(substitution_violations)
    blockers.extend(security_errors)

    if "dependency_change" in risks and (
        "data_source_change" in risks or "user_facing_output_change" in risks
    ):
        warnings.append(
            "dependency diff also touches data sources or user-facing output; verify Scope Lock explicitly."
        )

    status = "PASS"
    if blockers:
        status = "BLOCKED"
    elif warnings:
        status = "PASS_WITH_WARNINGS"

    return {
        "status": status,
        "changedFiles": files,
        "runtimeChangedFiles": runtime_files,
        "riskClasses": risks,
        "missingContracts": missing,
        "placeholderContracts": placeholders,
        "aliasTargetErrors": alias_target_errors,
        "blockers": blockers,
        "warnings": warnings,
        "gates": {
            "aliasTargets": "BLOCKED" if alias_target_errors else "PASS",
            "scopeLock": "BLOCKED" if missing or substitution_violations or (self_adopted and placeholders) else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
            "dataAuthenticity": "BLOCKED" if substitution_violations else "PASS",
            "goldenFlows": "BLOCKED" if ".pfo/GOLDEN_FLOWS.md" in missing or (self_adopted and ".pfo/GOLDEN_FLOWS.md" in placeholders) else ("PASS_WITH_WARNINGS" if ".pfo/GOLDEN_FLOWS.md" in placeholders else "PASS"),
            "regressionContract": "BLOCKED" if ".pfo/PROJECT_CONTRACT.md" in missing or (self_adopted and ".pfo/PROJECT_CONTRACT.md" in placeholders) else ("PASS_WITH_WARNINGS" if ".pfo/PROJECT_CONTRACT.md" in placeholders else "PASS"),
            "fallbackPolicy": "BLOCKED" if ".pfo/FALLBACK_POLICY.md" in missing or substitution_violations or (self_adopted and ".pfo/FALLBACK_POLICY.md" in placeholders) else "PASS",
            "diffRisk": "PASS_WITH_WARNINGS" if warnings else "PASS",
            "securityEvidence": "BLOCKED" if security_errors else "PASS",
            "noSilentSubstitution": "BLOCKED" if substitution_violations else "PASS",
            "executionPolicy": "BLOCKED" if ".pfo/EXECUTION_POLICY.json" in missing or execution_json_errors else "PASS",
            "permissionMatrix": "BLOCKED" if ".pfo/PERMISSION_MATRIX.md" in missing or ".pfo/PERMISSION_MATRIX.json" in missing or permission_json_errors else "PASS",
            "verificationContract": "BLOCKED" if ".pfo/VERIFICATION_CONTRACT.json" in missing or verification_json_errors else "PASS",
            "learningPromotion": "BLOCKED" if ".pfo/LEARNING_PROMOTION_GATE.md" in missing else "PASS",
            "toolCapabilityRegistry": "BLOCKED" if ".pfo/TOOL_CAPABILITY_REGISTRY.json" in missing or tool_json_errors else "PASS",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Product Factory OS project contract gates.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", action="store_true", help="Write PFO_CONTRACT_GATE.json into the project.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero on warnings as well as blockers.")
    args = parser.parse_args()

    project = args.project.resolve()
    if not project.is_dir():
        fail(f"project does not exist: {project}")

    result = evaluate(project)
    if args.write:
        (project / "PFO_CONTRACT_GATE.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"{result['status']}: PFO contract gate")
        if result["riskClasses"]:
            print("Risks: " + ", ".join(result["riskClasses"]))
        for item in result["warnings"]:
            print(f"WARNING: {item}")
        for item in result["blockers"]:
            print(f"BLOCKER: {item}")

    if result["status"] == "BLOCKED" or (args.strict and result["status"] != "PASS"):
        sys.exit(1)


if __name__ == "__main__":
    main()
