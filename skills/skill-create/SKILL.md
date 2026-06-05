---
name: skill-create
description: Create or update Product Factory OS skills using the skill-creator methodology, including SKILL.md design, reusable scripts/references/assets, PFO contracts, trigger coverage, route snapshots, and validation gates. Use when extending PFO with a new workflow, domain pack, client-specific process, connector workflow, premium pack skill, or when improving an existing PFO skill.
argument-hint: skill idea, target workflow, examples, or existing skill path
license: MIT
metadata:
  category: methodology
  tags: [skill, extension, workflow, methodology]
  effort: high
  side_effect: methodology-write
  explicit_invocation: false
---

# Skill Create

Use this skill to add or revise Product Factory OS skills without drifting from PFO contracts.

## Inputs To Collect

Ask only for details that change the skill:

- Skill purpose and target user request.
- 2 or 3 concrete prompts that should trigger it.
- Expected output artifacts.
- Side effects: read-only, writes docs, writes code, external tool writes, or production impact.
- Whether reusable `scripts/`, `references/`, or `assets/` are needed.
- Whether this belongs in core PFO, a client pack, or a premium/domain pack.

If examples are obvious from the request, proceed with conservative assumptions and record them.

## Process

1. Normalize the name to lowercase hyphen-case under 64 characters.
2. Decide degree of freedom:
   - High: concise text instructions for judgment-heavy workflows.
   - Medium: structured checklist plus references for repeatable workflows.
   - Low: scripts for fragile or deterministic operations.
3. Keep `SKILL.md` lean. Put long schemas, policies, examples, or provider-specific details in `references/`.
4. Use `scripts/` only for repeated or fragile operations that benefit from deterministic execution.
5. Use `assets/` only for templates or files copied into outputs.
6. For a new routable PFO skill, prefer the scaffold command, then edit the result:

   ```bash
   python3 scripts/pfo.py skill-scaffold <skill-name> \
     --description "<what it does and when to use it>" \
     --trigger "<natural language trigger>" \
     --output "<expected output>" \
     --expected-file "<expected artifact or NONE>"
   ```

7. Create or update:
   - `skills/<skill>/SKILL.md`
   - `docs/SKILL_CONTRACTS.md`
   - `docs/TRIGGERS.md`
   - `docs/CALL_GRAPH.md` when the skill is routable
   - `hooks/route-reminder.py` when natural-language routing should suggest it
   - `tests/snapshots/route-snapshots.json`
   - `tests/fixtures/<fixture>/idea.md`
   - `tests/fixtures/<fixture>/notes.md`
   - `tests/fixtures/<fixture>/expected-files.txt`
   - `scripts/validate_structure.py` required skill and fixture lists when the skill is core PFO
8. Update README or marketplace metadata when the public capability set changes.
9. Run validation.

## PFO Skill Shape

Use the local PFO frontmatter pattern:

```yaml
---
name: skill-name
description: Clear capability and trigger contexts.
argument-hint: short input hint
license: MIT
metadata:
  category: category
  tags: [tag-one, tag-two]
  effort: low|medium|high
  side_effect: read-only|docs-write|code-write|external-write|production-impact
  explicit_invocation: false
---
```

The `description` is the main trigger surface. Include what the skill does and when to use it.

## Fixture Shape

Create a minimal fixture:

````markdown
# Fixture: Skill Name

User request:

```text
Create a PFO skill for recurring customer interview synthesis.
```

Expected route:

```text
/task -> /skill-create
```
````

Use `expected-files.txt` to list expected artifacts, or `NONE` for read-only skills.

## Validation

Run the narrow gate first:

```bash
python3 hooks/skill-completeness.py --skill <skill>
```

Then run repository gates:

```bash
python3 scripts/validate_structure.py
python3 scripts/run_fixtures.py
python3 scripts/verify_fixture_contracts.py
python3 scripts/run_headless_fixtures.py --mode mock --fixture <fixture>
python3 scripts/validate_hooks.py
python3 scripts/meta_review.py
```

For high-risk, complex, or public-release skills, run a live forward-test on 2 or 3 representative fixtures when Codex auth and budget are available:

```bash
python3 scripts/run_headless_fixtures.py --mode command \
  --fixture <fixture-a> \
  --fixture <fixture-b> \
  --output-root .pfo-headless-runs/live \
  --command-template 'python3 {root}/scripts/pfo_headless_adapter.py'
```

Treat live output as a comparator surface: inspect `.pfo-headless-runs/live/PFO_HEADLESS_COMPARISON.md` and each `logs/comparison.md`, then tighten `SKILL.md`, bundled resources, or the output contract if the skill only works with leaked context.

## Self-validation

Before final output, verify:

- Route, side-effect, and confirmation requirements match metadata.
- Required artifacts or read-only result are explicit.
- Mock headless fixture validation passes for changed routable skills.
- Live forward-test expected/actual comparison is recorded for high-risk skills, or the auth/budget blocker is stated.
- Verification, blockers, and next route are stated.

## Rules

- Do not create auxiliary docs such as README, quick reference, or changelog inside the skill folder.
- Do not duplicate long reference material in `SKILL.md`.
- Do not add a routable core skill without contract, trigger, fixture, and snapshot coverage.
- Ask before overwriting an existing skill.
- Preserve existing PFO style unless the change intentionally updates the methodology.
- Treat production-impacting or external-write skills as requiring explicit confirmation.

## Done Criteria

- The skill has clear trigger metadata and concise operating instructions.
- Reusable resources are present only when they reduce repeated work or risk.
- PFO contracts, triggers, call graph, route snapshot, and fixture are synchronized.
- Validation passes or remaining failures are reported with exact blockers.
