# Dashboard

`dashboard/index.html` is a static Product Factory OS workspace health dashboard.

Generate metrics:

```bash
python3 scripts/pfo.py metrics --workspace /home/hihol/projects > dashboard/metrics.json
```

The page is dependency-free and reads `dashboard/metrics.json` when it exists.
It shows context index/snapshot coverage, live blocked project ratio, blockers by type,
stale state, missing gates, and live eval status.

Dashboard metrics are a read-only projection of local PFO state. They do not replace `pfo validate`, `.pfo/` contract gates, hook validation, or release checks.
