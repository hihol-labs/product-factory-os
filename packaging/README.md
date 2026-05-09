# Packaging

Install or refresh the local Product Factory OS checkout:

```bash
bash install.sh
```

If the repository is outside the workspace:

```bash
bash install.sh --workspace ~/Projects
```

The installer validates runtime contracts, installs the `pfo` command wrapper, installs hooks, writes workspace policy files, and adopts existing first-level projects by creating `AGENTS.md`, `CODEX.md`, `.codex-memory/`, and `.pfo/` contracts where missing.

Run release checks:

```bash
python3 scripts/release_check.py
```
