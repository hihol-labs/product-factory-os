# Dependency Audit Rubric

Dependency audits are read-only unless the user asks for remediation.

## Inputs

- `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`
- `pyproject.toml`, `requirements*.txt`, `poetry.lock`, `uv.lock`
- `go.mod`, `go.sum`
- `Cargo.toml`, `Cargo.lock`
- Dockerfiles and CI manifests

## Critical

- Known critical CVE in a production dependency with reachable usage.
- Malware/advisory package.
- License conflict that blocks intended distribution.
- Dependency install requires untrusted script execution not documented or pinned.

## Important

- High-severity CVE with available upgrade.
- Abandoned package in a security-sensitive path.
- Duplicate major frameworks that increase maintenance risk.
- Unpinned runtime base image.
- Lockfile missing for deployable apps.

## Recommended

- Add automated audit command to CI.
- Pin Docker base images by digest for production.
- Remove unused dependencies.
- Consolidate duplicate tooling.

