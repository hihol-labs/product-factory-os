# Diff Risk Classifier

Purpose: make the risk profile of a change visible before merge/deploy.

Universal risk classes:

- `dependency_change`
- `business_logic_change`
- `data_source_change`
- `provider_integration_change`
- `user_facing_output_change`
- `security_change`
- `deployment_change`
- `test_only_change`
- `documentation_change`

Universal rule:

- A narrow task may still be blocked if its diff crosses into a higher-risk class.
- Dependency fixes that also change data sources or user-facing output require explicit scope approval.

Gate output:

- `PASS`: risk classes match the task scope.
- `PASS_WITH_WARNINGS`: risk classes are broad but no forbidden substitution is detected.
- `BLOCKED`: risk classes contradict scope or project contracts.

