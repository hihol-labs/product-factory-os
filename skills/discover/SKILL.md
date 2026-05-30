---
name: discover
description: Product discovery workflow that turns an idea into market, user, scope, hypothesis, and validation notes.
argument-hint: idea, problem, market, or product hypothesis
license: MIT
metadata:
  category: planning
  tags: [discovery, product, market, mvp]
  effort: high
  side_effect: docs-write
  explicit_invocation: false
---

# Discover

Create `DISCOVERY.md`, `IDEA_SCORECARD.md`, and `VALIDATION_PLAN.md` for a product idea.

Use `/market-scan` before scoring when the idea has public market risk, competitor risk, ICP uncertainty, launch uncertainty, or depends on current user/community demand.

## Process

1. Clarify target user, painful problem, current alternatives, budget, timeline, and success metric.
2. Run `/market-scan` when fresh public market or community signals can affect the score.
3. Score the idea by pain, urgency, segment clarity, willingness to pay or adopt, audience access, validation speed, complexity, and strategic fit.
4. Run the evidence quality gate:
   - count real user conversations by segment;
   - separate past behavior evidence from opinions or hypothetical future intent;
   - record contradicting evidence;
   - state what must be true before the idea can receive `BUILD`.
5. Run adversarial discovery: why the idea may be wrong, why a competitor may win, which alternatives users already use, and which uncomfortable signals are being ignored.
6. Decide `KILL`, `TEST`, or `BUILD`.
7. Identify user segments and primary persona.
8. Summarize alternatives and differentiation.
9. Define the riskiest assumptions and validation experiments.
10. Design customer discovery around concrete past behavior, not "would you use this?" questions.
11. Prioritize features with MoSCoW and a lightweight RICE score.
12. Define the MVP scope, non-goals, and kill criteria.

## Output

Write or update:

`IDEA_SCORECARD.md` with:

- Candidate idea
- Target segment
- Evidence-backed score
- Evidence quality gate: real conversations, past behavior, contradicting evidence, and BUILD truth conditions
- Weaknesses to test first
- KILL, TEST, or BUILD decision

`VALIDATION_PLAN.md` with:

- Core hypothesis
- Customer discovery interview profile, forbidden questions, and five-interview debrief
- Riskiest assumptions
- Experiments
- Expected and actual signals
- Continue, pivot, or stop decision

`DISCOVERY.md` with:

- Problem statement
- Target users
- Customer discovery plan
- Jobs to be done
- Alternatives and competitors
- Positioning
- Hypotheses
- MVP scope
- Feature priority table
- Kill criteria
- Risks and unknowns

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Verification, blockers, and next route are stated.

## Rules

- If facts are unknown, mark them as assumptions.
- Do not invent market numbers without research.
- Do not invent recent social, competitor, or community signals. Use `/market-scan` or mark evidence as missing.
- Do not treat future-intent answers like "I would use this" as strong validation.
- Do not let `BUILD` scope pass when the scorecard still says `KILL`.
- Do not let `BUILD` scope pass without contradicting evidence or an explicit no-evidence exception.
- Ask before overwriting existing discovery or validation docs.
