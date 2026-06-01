# AGENTS

<!-- PFO_PROJECT_RUNTIME_START -->
## Product Factory OS Runtime

This existing project is adopted into Product Factory OS.

- Workspace: `/home/hihol/projects`
- Methodology: `/home/hihol/projects/product-factory-os`
- Project: `/home/hihol/projects/product-factory-os`

Before implementation, Codex must enforce full PFO adoption automatically:

```bash
pfo adopt /home/hihol/projects/product-factory-os
```

Then route work through `/task`, write `HANDOFF.md` before session or role transfer, update `.codex-memory/STATE.json`, and respect `.pfo/` contracts. Codex `/goal` mode is default-on for non-trivial work: create or continue the goal before implementation, and keep it active through gates, verification, and state-save. Project-local rules may add constraints, but they do not replace PFO gates, memory, or scope/data/degraded-mode contracts. Keep local rules short and earned: add them only for observed failures or hard external constraints.
<!-- PFO_PROJECT_RUNTIME_END -->
