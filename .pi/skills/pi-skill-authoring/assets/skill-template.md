---
name: skill-name
description: One sentence on what the skill does. Then when to use it, with concrete trigger cues. Use when the user asks to ..., mentions ..., or wants ... — even if they do not name this skill explicitly.
---

# Skill Title

One or two lines orienting the model: what this skill produces and the key mental model.
Skip anything Pi already knows.

## Workflow

1. **First step** — what to do, and what to check.
2. **Second step** — explain *why* where the reason is not obvious.
3. **Third step** — point at bundled files with paths relative to this skill directory:
   read `references/details.md` before doing X; run `scripts/helper.sh` instead of
   reimplementing Y.

## Decision points

| Situation | Do this |
|---|---|
| Common case A | ... |
| Case B | ... |

## Output format

Use this template verbatim (or show an Input/Output example pair) when the format matters:

```text
# [Title]
## Section
```

## Edge cases and gotchas

- Things that break, and what to do instead.
- Keep this section short; move long reference material to `references/`.
