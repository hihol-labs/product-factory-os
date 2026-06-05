# Forbidden Changes

These changes are blocked unless explicitly approved in the task scope.

## Always Forbidden Without Explicit Scope

- Replacing real data with synthetic data.
- Labeling mock/demo/fixture/fallback data as real production output.
- Changing user-facing semantics while working on a dependency-only or infrastructure-only task.
- Bypassing provider, auth, billing, payment, compliance, or security checks.
- Removing tests or quality gates to make a build pass.

## Project-Specific Forbidden Changes

- Do not weaken adoption, contract gates, self-contract validation, state-save, or production readiness to make a report pass.
- Do not classify generated PFO status/report files as product implementation changes.
- Do not require users to run setup commands manually when the PFO runtime can install, adopt, analyze, or report automatically.
- Do not remove security evidence requirements for real security-sensitive source, config, provider, permission, or deployment changes.
- Do not overwrite project-owned instructions outside managed PFO runtime blocks.
