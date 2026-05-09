# Public Roadmap Issues

Use these as public roadmap issues after the `0.6.1` workspace-runtime install pass.

## 1. Harden installer update flow

Labels: `type:roadmap`, `area:runtime`

Acceptance:

- `install.sh` supports update mode in addition to current install/adopt behavior.
- The install docs cover local, cloned, and released usage.
- A smoke test verifies install from GitHub release artifacts.

## 2. Add plugin packaging and publishing workflow

Labels: `type:roadmap`, `area:runtime`

Acceptance:

- Plugin packaging steps are documented.
- Manifest validation covers marketplace-facing metadata.
- Release checklist includes packaging validation.

## 3. Expand generated project validators

Labels: `type:feature`, `area:runtime`

Acceptance:

- Generated projects validate `QUALITY_GATES.md`, starter compliance, and state consistency.
- `pfo new -> pfo plan -> pfo validate` passes for every open-source starter pack.
- Validation reports actionable failures.

## 4. Build a full generated SaaS reference project

Labels: `type:roadmap`, `area:starters`

Acceptance:

- A reference SaaS project is generated with PFO.
- It includes backend, frontend, tests, deploy docs, and PFO state.
- The example is documented under `docs/examples/`.

## 5. Add premium starter pack boundary tests

Labels: `type:roadmap`, `area:commercial`

Acceptance:

- Open-source and premium-pack boundaries are explicit.
- Open-source validation does not require premium assets.
- Commercial docs explain ownership and extension rules.

## 6. Add voice workflow examples and docs

Labels: `type:docs`, `area:runtime`

Acceptance:

- Voice-first commands cover new project and existing project workflows.
- Examples show route, state, artifact, and next action.

## 7. Add marketplace publishing checklist

Labels: `type:docs`, `area:runtime`

Acceptance:

- Marketplace metadata checklist exists.
- Release process references publishing steps.

## 9. Promote hook parity to default local workflow

Labels: `type:feature`, `area:hooks`

Acceptance:

- `scripts/validate_hooks.py` runs in CI.
- Hook installation is documented for Codex Desktop and CLI-like environments.
- Route snapshots remain mandatory for every skill.

## 10. Expand runtime executor beyond state recording

Labels: `type:feature`, `area:runtime`

Acceptance:

- `pfo build`, `pfo test`, and `pfo review` can execute or propose concrete commands from starter contracts.
- Execution history records command, result, duration, and evidence.
- Failed nodes produce repair paths in state.

## 8. Add cloud/team workspace design draft

Labels: `type:roadmap`, `area:commercial`

Acceptance:

- Cloud/team workspace architecture is described.
- Hosted dashboard, managed execution, policy, and billing boundaries are clear.
