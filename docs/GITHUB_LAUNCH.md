# GitHub Launch Checklist

Use this checklist after pushing Product Factory OS to GitHub.

## Repository Settings

Recommended repository:

```text
hihol-labs/product-factory-os
```

Recommended description:

```text
Product Factory OS for Codex: deterministic runtime for turning product ideas into blueprint, execution graph, gated build, tests, deploy readiness, and reloadable state.
```

Recommended topics:

```text
codex, product-factory, ai-agents, product-engineering, execution-engine, scaffolding, open-core, developer-tools
```

Enable:

- Issues
- Discussions
- Wiki disabled unless documentation moves there
- Actions

## Release

Create the next release from tag `v0.6.0` with notes from:

```text
docs/RELEASE_NOTES_v0.6.0.md
```

## Roadmap Issues

Create these initial issues:

1. Harden installer and update flow
2. Add plugin packaging and publishing workflow
3. Expand generated project validators
4. Build a full generated SaaS reference project
5. Add premium starter pack boundary tests
6. Add voice workflow examples and docs
7. Add marketplace publishing checklist
8. Add cloud/team workspace design draft

## Optional gh Commands

Run these after `gh auth login` works:

```bash
gh repo edit hihol-labs/product-factory-os \
  --description "Product Factory OS for Codex: deterministic runtime for turning product ideas into blueprint, execution graph, gated build, tests, deploy readiness, and reloadable state." \
  --homepage "https://github.com/hihol-labs/product-factory-os" \
  --enable-issues \
  --enable-discussions

gh repo edit hihol-labs/product-factory-os \
  --add-topic codex \
  --add-topic product-factory \
  --add-topic ai-agents \
  --add-topic product-engineering \
  --add-topic execution-engine \
  --add-topic scaffolding \
  --add-topic open-core \
  --add-topic developer-tools

gh release create v0.6.0 --repo hihol-labs/product-factory-os \
  --title "Product Factory OS v0.6.0" \
  --notes-file docs/RELEASE_NOTES_v0.6.0.md
```
