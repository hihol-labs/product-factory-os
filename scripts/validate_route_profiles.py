#!/usr/bin/env python3
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "routing" / "route-profiles.json"
PROFILE_IDS = ["minimal", "standard", "full"]
MINIMAL_STEPS = ["adoption", "scope", "targetedVerification", "review", "stateSave"]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
    data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profiles = data.get("profiles")
    if data.get("defaultProfile") != "standard":
        fail("route profiles defaultProfile must be standard")
    if not isinstance(profiles, dict):
        fail("route profiles must define profiles object")
    for profile_id in PROFILE_IDS:
        profile = profiles.get(profile_id)
        if not isinstance(profile, dict):
            fail(f"missing route profile {profile_id}")
        for field in [
            "label",
            "intendedFor",
            "selectionHints",
            "steps",
            "gates",
            "requiredArtifacts",
            "optionalArtifacts",
            "forbiddenArtifacts",
            "verificationPolicy",
        ]:
            if field not in profile:
                fail(f"profile {profile_id} missing {field}")
        for field in ["selectionHints", "steps", "gates", "requiredArtifacts"]:
            if not isinstance(profile.get(field), list) or not profile[field]:
                fail(f"profile {profile_id}.{field} must be a non-empty list")
        policy = profile.get("verificationPolicy")
        if not isinstance(policy, dict):
            fail(f"profile {profile_id}.verificationPolicy must be an object")
        if not policy.get("mode"):
            fail(f"profile {profile_id}.verificationPolicy missing mode")
        commands = policy.get("defaultCommands")
        if not isinstance(commands, list) or not commands:
            fail(f"profile {profile_id}.verificationPolicy.defaultCommands must be a non-empty list")

    minimal = profiles["minimal"]
    if minimal.get("steps") != MINIMAL_STEPS:
        fail("minimal route must run exactly adoption, scope, targetedVerification, review, stateSave")
    forbidden = set(minimal.get("forbiddenArtifacts", []))
    for artifact in ["PRODUCT_BLUEPRINT.md", "BUILD_PLAN.md", "EXECUTION_GRAPH.md", "TEST_PLAN.md", "QUALITY_GATES.md"]:
        if artifact not in forbidden:
            fail(f"minimal route must forbid overhead artifact {artifact}")
    if "production_readiness" in " ".join(minimal["verificationPolicy"]["defaultCommands"]):
        fail("minimal route must not run production readiness by default")

    print("OK: route profiles validated")


if __name__ == "__main__":
    main()
