# Skill Writing Guide

How to write a `SKILL.md` body that Pi will actually follow, and how to structure the
supporting files around it.

## Table of contents

- [Progressive disclosure](#progressive-disclosure)
- [Body structure](#body-structure)
- [Writing style](#writing-style)
- [Common patterns](#common-patterns)
- [Bundled resources](#bundled-resources)
- [Anti-patterns](#anti-patterns)

## Progressive disclosure

Three levels load at different times:

1. **Metadata** (`name` + `description`) — always in context, roughly 100 tokens per skill.
   This is the only thing the model sees when deciding whether to load the skill.
2. **`SKILL.md` body** — loaded when the skill triggers. Recommended under 5,000 tokens
   (~500 lines).
3. **Bundled resources** — read only when needed; scripts can run without being read into
   context at all.

Consequences for how you write:

- All "when to use this" information goes in the `description`, not the body. By the time
  the body is loaded, the triggering decision has already been made.
- The body should start with the workflow, not with background the model already has.
- Long reference material moves to `references/*.md` with a clear pointer: "Read
  `references/formats.md` before converting a document." Keep references one level deep
  from `SKILL.md`; do not build reference chains.
- For a reference file over ~300 lines, add a table of contents.

## Body structure

A body that works well usually has:

- **A one- or two-line orientation** stating what the skill produces and the key mental
  model. Skip pleasantries.
- **A numbered workflow** for multi-step tasks, or grouped sections for reference-style
  skills. Steps say what to do and what to check, not what to think about.
- **Decision points** as small tables or short bullet lists ("If X, do A; if Y, do B").
- **Examples** of input → output wherever the format is not obvious.
- **Edge cases and gotchas** near the end, where they do not interrupt the main flow.

Use `##` for major sections and `###` sparingly. Deeply nested headings signal a file that
should have been split.

## Writing style

- **Imperative form.** "Read the config", not "The config should be read".
- **Explain why.** Today's models have good theory of mind. "Use a temp file because the
  target directory is read-only in CI" beats "ALWAYS use a temp file". If you find yourself
  writing ALL-CAPS MUST/NEVER or rigid scaffolding, treat it as a yellow flag: reframe and
  give the reasoning.
- **Address the model directly.** "Pi" or "you" is fine; pick one and stay consistent.
- **Be concrete.** Name actual commands, paths, file names, and field names from this
  project rather than describing them abstractly.
- **Stay general enough to reuse.** The skill will run on prompts you have never seen. Do
  not hard-code one example's specifics into the instructions.
- **Cut ruthlessly.** Every line costs context on every invocation. If a sentence does not
  change what the model does, delete it.

## Common patterns

Defining an exact output format:

```markdown
## Report structure
Use this template verbatim:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

Input/output examples — useful for format-sensitive work like commit messages or parsing:

```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

Pointing at a script instead of describing an algorithm:

```markdown
## Generating the index
Run `python3 <this-skill-dir>/scripts/build_index.py <src-dir>`. It writes `index.json`
and prints a summary. Read the script only if it fails.
```

Domain organization — one selection workflow in `SKILL.md`, variants in `references/`:

```text
cloud-deploy/
├── SKILL.md            # workflow + how to pick a provider
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

The model reads only the relevant variant file.

## Bundled resources

- `scripts/` — deterministic or repetitive work: parsing, generation, validation, API
  calls. Bundle a script when you notice runs reinventing the same helper. Scripts should
  be self-contained or document their dependencies, print helpful errors, and handle edge
  cases. Bash, Python, and Node are the common choices; declare anything unusual in
  `compatibility`.
- `references/` — docs loaded on demand. Keep each file focused on one topic so reading it
  costs little context.
- `assets/` — files used in the output: templates, schemas, sample configs, images.

Refer to bundled files with paths relative to the skill directory. Pi tells the model where
the skill lives so it can resolve them; absolute machine-specific paths break sharing.

## Anti-patterns

- **Vague descriptions.** "Helps with PDFs" carries no routing signal. Say what it does and
  when it applies.
- **Trigger conditions buried in the body.** The model has not read the body yet when it
  decides.
- **Everything in one file.** A 900-line `SKILL.md` taxes every invocation; split into
  references.
- **Narrating the obvious.** Restating what tools do, or listing steps the model would take
  anyway, wastes context and dilutes the instructions that matter.
- **Over-constraining.** Ten MUSTs produce brittle behavior on prompts you did not test.
  Explain the goal and the reason.
- **Overfitting to test cases.** Patching the specific examples you ran instead of
  generalizing the underlying instruction.
- **Unreviewed scripts.** Project skills can run commands and edit files under project
  trust. Anything destructive belongs behind `disable-model-invocation: true`.
- **Surprising intent.** A skill's contents should not surprise the user if described to
  them. Never write skills that hide exfiltration, unauthorized access, or misleading
  behavior.
