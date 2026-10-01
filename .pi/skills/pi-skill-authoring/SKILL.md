---
name: pi-skill-authoring
description: Author, review, and improve Agent Skills for the Pi coding agent. Use whenever the user wants to create a new skill, turn a repeated workflow into a skill, edit or debug an existing SKILL.md, write a skill description that triggers reliably, decide between a skill vs prompt template vs extension, validate a skill directory, or package skills into a Pi package. Trigger even when the user does not say the word "skill" but describes capturing reusable agent instructions (e.g. "make pi always do X when...", "save this workflow so you reuse it").
---

# Pi Skill Authoring

Skills are directories containing `SKILL.md` that give Pi specialized instructions plus
supporting files. Pi advertises only each skill's `name` and `description` at startup and
loads the full body when a task matches, so the description is the routing mechanism and
the body is the payoff. Write both for that split.

Figure out where the user is in the process — new skill, existing skill to improve, or a
skill that is not triggering — and join them there instead of restarting the workflow.

## Step 1: Capture intent

Extract answers from the conversation first; the user may be asking you to capture a
workflow you just performed together. Confirm before writing files. Ask only about what
the conversation does not already answer:

1. What should the skill make Pi able to do?
2. When should it trigger — what user phrasings, file types, project situations?
3. What is the expected output or end state?
4. What does Pi need that it does not already have: commands, scripts, templates, domain
   facts, project conventions?
5. Is this really a skill? See "Choose the right mechanism" below.

Prefer a narrow skill that fires reliably over a broad one that competes with everything.
If the request covers several unrelated workflows, propose splitting it.

## Step 2: Check the mechanism

| Need | Use |
|---|---|
| Reusable instructions, possibly with scripts/references/assets, loaded on demand | **Skill** (this guide) |
| A reusable prompt as a `/command`, no supporting files | Prompt template (`docs/prompt-templates.md`) |
| New tool, event hook, TUI component, custom provider | Extension (`docs/extensions.md`) |
| Share skills/extensions/themes through npm or git | Pi package (`docs/packages.md`) |

If the user wants executable integration, stop and point them at extensions rather than
stuffing behavior into a skill.

## Step 3: Create the directory

Project skills live in `.pi/skills/<name>/`; Pi also discovers `.agents/skills/<name>/`
(portable across Agent Skills implementations) from the working directory up to the repo
root. Personal skills live in `~/.pi/agent/skills/<name>/` or `~/.agents/skills/<name>/`.
Discovery is recursive, and the directory name must match the frontmatter `name`.

```text
.pi/skills/<name>/
├── SKILL.md          # required: frontmatter + instructions
├── scripts/          # executables for deterministic or repetitive steps
├── references/       # docs read on demand
└── assets/           # templates and files used in output
```

Start from `assets/skill-template.md` in this skill directory (copy it, then edit), or
write from scratch following `references/writing-guide.md`.

## Step 4: Write the frontmatter

Only `name` and `description` are required. Read `references/frontmatter.md` for every
field, its constraints, and how Pi behaves when something is malformed (mostly warnings,
except a missing description, which prevents loading).

Frontmatter rules that matter most:

- `name`: lowercase letters, numbers, hyphens; no leading/trailing/consecutive hyphens;
  max 64 chars; must equal the parent directory name.
- `description`: max 1024 chars; must state what the skill does **and** when to use it.
  Pi tends to under-trigger, so include concrete trigger cues ("Use when the user mentions
  X, Y, even if they do not say 'skill'").
- `disable-model-invocation: true` when the skill should only run via `/skill:name`.

## Step 5: Write the body

Keep `SKILL.md` under 500 lines. Everything longer belongs in `references/*.md` with an
explicit pointer telling the model when to read that file. Reference bundled files with
paths relative to the skill directory — Pi tells the model where the skill lives so it can
resolve them.

Read `references/writing-guide.md` for the full guide: progressive disclosure, imperative
style, explaining *why* instead of stacking MUSTs, examples format, domain organization,
and the anti-patterns that make skills fail.

Non-negotiables: no malware, exploit code, credential harvesting, or content that would
surprise the user if described to them. Project skills can instruct Pi to run scripts and
modify files, so they are trusted code — write them that way.

## Step 6: Validate

Run the bundled validator from the skill directory:

```bash
python3 <this-skill-dir>/scripts/validate_skill.py <path-to-skill-dir>
```

It checks frontmatter presence and field constraints, name/directory agreement, body
length, broken relative file references, and missing descriptions. Pass a directory of
skills to check them all.

Then verify Pi actually loads it:

1. Run `/reload` in an active session (or restart Pi from a directory where the skill is
   discoverable) and check startup diagnostics for warnings.
2. Confirm `/skill:<name>` appears and loads the right instructions.
3. Check name collisions — Pi keeps the first discovered skill and warns.

## Step 7: Test with real prompts

Write 2–3 prompts a real user would type, including at least one that should *not* trigger
the skill, and confirm them with the user before running. Read `references/testing.md` for
the test-and-iterate loop, trigger evaluation, and how to review results.

After testing, re-read the body with fresh eyes and cut anything that did not pull its
weight.

## Step 8: Iterate

Generalize from feedback rather than patching the specific examples you tested. If every
test run had Pi write the same helper script, bundle it in `scripts/`. If a stubborn
behavior persists, change the framing or explain the reasoning instead of adding another
capitalized rule. Keep the prompt lean: remove instructions that do not change outcomes.

## Distributing

Keep environment setup inside the skill and declare runtime dependencies in a Pi package
(`docs/packages.md`). Pi supplies `@earendil-works/pi-ai`, `@earendil-works/pi-agent-core`,
`@earendil-works/pi-coding-agent`, `@earendil-works/pi-tui`, and `typebox` to extensions
and skills.
