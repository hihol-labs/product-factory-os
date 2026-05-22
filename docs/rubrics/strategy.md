# Strategy Rubric

Use this rubric from `/strategy` and `/advisor` when product direction, market, roadmap, monetization, or launch decisions matter.

## Critical

| ID | Check | Pass Criteria |
|---|---|---|
| S1 | Problem clarity | The target problem is specific, painful, and tied to a user segment. |
| S2 | ICP | The ideal customer profile or primary user segment is explicit. |
| S3 | MVP scope | The first release has a small, testable scope with non-goals. |
| S4 | Value proposition | The product has a clear reason to exist versus alternatives. |
| S5 | Success metric | The next milestone has measurable success criteria. |
| S6 | Monetization or value capture | Revenue, savings, retention, lead capture, or other value capture is explicit when relevant. |
| S7 | Acquisition path | At least one realistic path to first users or internal adoption is named. |
| S8 | Strategic risks | The top product, technical, legal, operational, and go-to-market risks are named with mitigations. |
| S9 | Idea gate | `IDEA_SCORECARD.md` has a KILL, TEST, or BUILD decision backed by evidence. |
| S10 | Validation plan | `VALIDATION_PLAN.md` names riskiest assumptions, experiments, expected signals, and exit decision. |
| S11 | Self-improvement loop | Autonomous improvement has one metric, fixed budget, protected evaluation files, baseline, and keep/discard/crash logging. |

## Important

| ID | Check | Pass Criteria |
|---|---|---|
| I1 | Competitive alternatives | Existing alternatives and substitutes are acknowledged. |
| I2 | Pricing hypothesis | Pricing or budget assumption is documented when money changes hands. |
| I3 | Launch sequence | The launch plan has stages, owner assumptions, and exit criteria. |
| I4 | Feedback loop | There is a plan to collect user feedback and measure behavior. |
| I5 | Roadmap discipline | Deferred features are captured without polluting MVP scope. |
| I6 | Funnel model | Acquisition, activation, conversion, and retention stages have metrics or explicit not-applicable notes. |
| I7 | Iteration evidence | Product changes reference feedback, metrics, validation evidence, or a recorded strategy decision. |
| I8 | Assetization | Reusable learnings can be promoted into `ASSET_REGISTER.md` or `CONTENT_BACKLOG.md` when appropriate. |

## Recommended

- Document assumptions as testable hypotheses.
- Record major strategy decisions as ADRs.
- Keep a dated backlog with priority and rationale.
- Do not count activity as progress unless it changes a signal, gate, asset, or decision.
- Use `.pfo/EXPERIMENT_PROGRAM.md` and `.pfo/EXPERIMENTS.tsv` for Autoresearch-style iteration.
