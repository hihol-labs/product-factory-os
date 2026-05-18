---
name: perf
description: Analyze and improve performance using measurement-first workflow.
argument-hint: slow endpoint, function, query, build, or user flow
license: MIT
metadata:
  category: daily-work
  tags: [performance, profiling, optimization]
  effort: high
  side_effect: code-write-optional
  explicit_invocation: false
---

# Performance

Optimize only after identifying the bottleneck.

## Process

1. Define the slow path and expected target.
2. Measure or inspect the likely bottleneck.
3. Identify algorithm, query, network, rendering, build, or resource issue.
4. Apply the smallest fix.
5. Re-measure when possible.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Avoid speculative rewrites.
- Preserve correctness and tests.
- Document tradeoffs and remaining bottlenecks.
