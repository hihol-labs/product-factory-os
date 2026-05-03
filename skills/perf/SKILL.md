---
name: perf
description: Analyze and improve performance using measurement-first workflow.
argument-hint: slow endpoint, function, query, build, or user flow
license: MIT
metadata:
  category: daily-work
  tags: [performance, profiling, optimization]
---

# Performance

Optimize only after identifying the bottleneck.

## Process

1. Define the slow path and expected target.
2. Measure or inspect the likely bottleneck.
3. Identify algorithm, query, network, rendering, build, or resource issue.
4. Apply the smallest fix.
5. Re-measure when possible.

## Rules

- Avoid speculative rewrites.
- Preserve correctness and tests.
- Document tradeoffs and remaining bottlenecks.

