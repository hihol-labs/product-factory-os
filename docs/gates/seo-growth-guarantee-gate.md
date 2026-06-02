# SEO Growth Guarantee Gate

This optional growth gate regulates SEO claims for a concrete product. It converts "SEO should grow traffic" into a measured experiment with baseline, target, source, window, shipped changes, exclusions, decision, and next iteration.

Canonical template:

```text
docs/templates/SEO_GROWTH_GUARANTEE_GATE.md
```

Validator:

```bash
python3 scripts/validate_seo_growth_gate.py /path/to/project
```

## Required Fields

- baseline metric
- target metric
- measurement source
- attribution window
- implemented changes
- exclusion factors
- result decision
- next iteration

## Gate Meaning

- `PENDING`: planned or in-flight measurement.
- `BLOCKED`: required evidence or approved data access is missing.
- `PASSED_WITH_WARNINGS`: result is measured, but attribution is noisy.
- `PASSED`: evidence supports the SEO result decision.

The gate guarantees measurement discipline, not external search-engine outcomes.
