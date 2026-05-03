---
name: project
description: Route new product/project creation requests through the Product Factory OS entry flow.
argument-hint: product idea or project description
license: MIT
metadata:
  category: router
  tags: [project, router, creation, methodology]
---

# Project Router

Use this skill when the user wants to create a new project, app, service, site, bot, MVP, CLI, scraper, mini app, e-commerce system, internal automation, or product from an idea.

## Instructions

1. Decide whether this is a new project or existing-code work.
2. If the user mentions stack traces, existing files, failing tests, current modules, or recent commits, route to `/task`.
3. Capture the initial Product Factory OS intent:
   - product type signal
   - domain
   - complexity signal
   - infrastructure signal
4. If this is new work, ask one route question unless the answer is already obvious:
   - `A` Full cycle: plan, implement, test, review, deploy.
   - `B` Planning only: create documents, no code.
   - `C` Existing docs: create an execution guide from current docs.
5. Route:
   - `A` -> `/kickstart`
   - `B` -> `/blueprint`
   - `C` -> `/guide`

## Rules

- Do not generate code or docs inside the router.
- Ask only the routing question. Clarifying product questions belong to the destination skill.
- Prefer route `A` when the user asks for a finished working project.
- For PFO requests, preserve the router-first path: idea -> `/project` -> `/blueprint` or `/kickstart`.
- Product classification is performed by the destination skill using `routing/product-classifier.json`.

## Self-Check

- The request was classified as new-project or existing-code work.
- Exactly one destination skill was selected.
- No implementation work was done by this router.
- Product Factory OS intent signals were preserved for the next skill.
