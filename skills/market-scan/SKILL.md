---
name: market-scan
description: Fresh public market and community signal scan for product discovery, validation, ICP, competitor, launch, and roadmap decisions. Use Last30Days when available.
argument-hint: idea, problem, segment, competitor, audience, or launch question
license: MIT
metadata:
  category: research
  tags: [market, discovery, validation, last30days, social-signals]
  effort: high
  side_effect: external-read-docs-write
  explicit_invocation: false
---

# Market Scan

Use this skill when PFO needs current public market, competitor, user, or community signals before a product or strategy decision.

Preferred research engine: `last30days` from `mvanhorn/last30days-skill`.

## Inputs

- Topic, idea, problem, segment, competitor, or launch question
- Target market or geography when relevant
- Product stage: discovery, blueprint, strategy, launch, or iteration
- Existing PFO artifacts if present: `DISCOVERY.md`, `IDEA_SCORECARD.md`, `VALIDATION_PLAN.md`, `MARKET_BRIEF.md`, `ICP.md`, `GO_TO_MARKET.md`, `FEEDBACK_LOG.md`

## Process

1. Read existing PFO artifacts before researching.
2. Convert the user request into a public-safe research topic. Remove secrets, private customer data, internal metrics, and proprietary snippets.
3. If `last30days` is installed, invoke it for the topic and use its synthesized evidence.
4. If `last30days` is unavailable, mark the scan `BLOCKED_EXTERNAL_TOOL` and list the exact research topic to rerun after installation. Do not fake social or market evidence.
5. Normalize findings into PFO artifacts. Do not paste raw Last30Days output wholesale.
6. Update decision impact:
   - `IDEA_SCORECARD.md`: evidence, weaknesses, KILL/TEST/BUILD impact.
   - `VALIDATION_PLAN.md`: Last 30 Days signal, source, engagement, confidence, next experiment.
   - `MARKET_BRIEF.md`: recent community signals, adversarial discovery, top complaints, alternatives, evidence links.
   - `FEEDBACK_LOG.md`: public feedback patterns when they influence iteration.
   - `CONTENT_BACKLOG.md`: public content candidates only when evidence is approved for reuse.

## Output Shape

Return:

```text
TOPIC:
FRESH SIGNALS:
TOP COMPLAINTS:
ALTERNATIVES:
ADVERSARIAL DISCOVERY:
CONFIDENCE:
PFO ARTIFACT IMPACT:
NEXT VALIDATION STEP:
```

When writing docs, append dated evidence instead of replacing prior user-authored research unless the user explicitly asks to rewrite.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- Public sources only.
- Do not send secrets, private customer data, unreleased product details, or proprietary code to external research tools.
- Cite source links when available.
- Separate verified evidence from assumptions.
- Surface competitor advantages and uncomfortable negative signals instead of only supportive evidence.
- Recent social engagement is a signal, not proof. Convert it into validation experiments before broad build scope.
