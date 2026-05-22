# Autoresearch Integration

PFO adopts the useful Autoresearch pattern as a general self-improvement loop for products, code, prompts, tests, performance, and methodology changes with a fixed budget.

Autoresearch's core idea is not the training code itself. The portable idea is a small autonomous research organization: fixed scope, protected evaluation, fixed time budget, one metric, baseline first, repeated candidate changes, and a keep/discard/crash decision log.

## PFO Mapping

| Autoresearch concept | PFO implementation |
|---|---|
| `program.md` as research-org code | `.pfo/EXPERIMENT_PROGRAM.md` |
| `train.py` as only editable surface | `.pfo/UNIT_CONTEXT_MANIFEST.json` `allowedWriteAreas` |
| `prepare.py` as protected harness | `.pfo/EXPERIMENT_PROGRAM.md` `protectedFiles` |
| fixed five-minute training budget | `pfo experiment-init --budget-seconds` |
| `val_bpb` as primary metric | `pfo experiment-init --metric --direction` |
| `results.tsv` | `.pfo/EXPERIMENTS.tsv` |
| keep/discard branch advancement | `pfo experiment-record --status auto|keep|discard|crash` plus `pfo finish-branch` when branch cleanup is in scope |
| simplicity criterion | `complexity_cost` in experiment records and quality review |
| repeated overnight loop | PFO AFK/delegated execution with handoff, recovery, and production-side-effect guardrails |

## Operating Contract

1. Initialize the loop:

```bash
pfo experiment-init <project> \
  --tag exp-YYYYMMDD \
  --metric primary_metric \
  --direction lower \
  --budget-seconds 300 \
  --run-command "pytest -q"
```

2. Record the baseline:

```bash
pfo experiment-record <project> \
  --metric-value 1.234567 \
  --status keep \
  --description "baseline"
```

3. For each candidate, change only allowed files, run the fixed command, then record:

```bash
pfo experiment-record <project> \
  --metric-value 1.210000 \
  --status auto \
  --complexity-cost 1 \
  --description "simplify validation path"
```

`auto` keeps the run only when the metric improves against the current best. Equal metric quality can still be kept manually when the code is simpler.

## Guardrails

- Evaluation harnesses, real data sources, `.pfo/` contracts, and golden flows are protected.
- Missing metric output is not success.
- Crashes are logged as failed experiments unless the repair is trivial and within scope.
- Production, infrastructure, migration, billing, DNS, and external-write operations still require explicit approval.
- Durable discoveries move through `.codex-memory/LEARNINGS.jsonl` and `memory/LEARNING_REGISTRY.json` before changing PFO methodology.
