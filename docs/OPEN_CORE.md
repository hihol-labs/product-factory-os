# Open Core Strategy

Product Factory OS uses an open-core model.

The goal is to make the local Product Factory Runtime broadly useful and trustworthy while keeping room for commercial extensions around premium templates, hosted collaboration, managed execution, and enterprise support.

## Open Source Core

The open source core includes:

- Runtime CLI
- Product classifier
- Product compiler contracts
- State machine
- Validators
- Hook contracts and local hook scripts
- Route snapshots and methodology fixtures
- Basic starter packs
- Basic golden paths
- Local dashboard shell
- Voice/text intent normalization
- Methodology skills
- Agent role prompts
- Quality rubrics
- Local memory/state format
- Local integration export contracts

As of `0.6.0`, the open-source runtime also includes the smoke-tested path:

```text
pfo new -> pfo plan -> pfo validate
```

This path is intentionally open source because trust in the product-runtime depends on local reproducibility.

## Commercial Extensions

Commercial extensions may include:

- Premium starter packs
- Hosted dashboard
- Team workspaces
- Approval workflows
- Organization memory
- Managed cloud execution
- Private template registry
- GitHub/Linear/Notion hosted sync
- Enterprise policy enforcement
- Support, onboarding, and implementation services

## Generated Products

Products generated with Product Factory OS belong to their authors.

Using PFO does not require generated products to be open source. Generated products may be private, commercial, internal, client-owned, or open source at the user's choice.

The PFO runtime is licensed separately from products created with it. Generated projects are not considered derivative works of PFO merely because PFO created scaffolding, plans, docs, state files, or validation artifacts.

## Boundary Rule

Open source code lives in this repository.

Commercial code, private premium packs, hosted services, customer data, and proprietary templates should live outside the open source repository unless intentionally published.
