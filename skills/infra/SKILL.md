---
name: infra
description: Generate infrastructure-as-code and deployment configuration.
argument-hint: platform, cloud, container, kubernetes, terraform, or service
license: MIT
metadata:
  category: operations
  tags: [infra, iac, docker, terraform, kubernetes]
  effort: high
  side_effect: infrastructure-write
  explicit_invocation: true
  skill_version: 1
  prompt_version: pfo-infra-v1
  eval_dataset: tests/eval-datasets/infra.json
---

# Infra

Generate infrastructure artifacts without calling cloud APIs.

## Outputs

Depending on target:

- `Dockerfile`
- `docker-compose.yml`
- `infra/terraform/`
- `infra/k8s/`
- `helm/`
- deployment README

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- No cloud mutations.
- No real secrets in generated files.
- Production state must use remote state and locking when Terraform is generated.
- Include verification and rollback notes.
