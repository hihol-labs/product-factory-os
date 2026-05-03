# Initial GitHub Issues

Use these as the first public roadmap issues.

## 1. Harden installer and update flow

Labels: `type:roadmap`, `area:runtime`

Acceptance:

- `packaging/install.sh` supports install and update modes.
- The install docs cover local and cloned usage.
- A smoke test verifies install from GitHub.

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

## 8. Add cloud/team workspace design draft

Labels: `type:roadmap`, `area:commercial`

Acceptance:

- Cloud/team workspace architecture is described.
- Hosted dashboard, managed execution, policy, and billing boundaries are clear.
