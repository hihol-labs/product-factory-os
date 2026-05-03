---
name: infra
description: Generate infrastructure-as-code and deployment configuration.
argument-hint: platform, cloud, container, kubernetes, terraform, or service
license: MIT
metadata:
  category: operations
  tags: [infra, iac, docker, terraform, kubernetes]
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

## Rules

- No cloud mutations.
- No real secrets in generated files.
- Production state must use remote state and locking when Terraform is generated.
- Include verification and rollback notes.

