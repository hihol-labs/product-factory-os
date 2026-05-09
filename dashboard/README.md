# Dashboard

`dashboard/index.html` is a static Product Factory OS dashboard shell.

Generate metrics:

```bash
python3 scripts/pfo.py metrics --workspace /home/hihol/projects > dashboard/metrics.json
```

The page is dependency-free and can be extended into a richer local UI.

Dashboard metrics are a read-only projection of local PFO state. They do not replace `pfo validate`, `.pfo/` contract gates, hook validation, or release checks.
