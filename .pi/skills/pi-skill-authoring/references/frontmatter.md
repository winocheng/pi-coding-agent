# Frontmatter Reference

Pi implements the [Agent Skills specification](https://agentskills.io/specification). Most
invalid fields produce warnings at startup rather than blocking load — but a malformed
`SKILL.md` or a skill without a description is **not loaded at all**.

## Table of contents

- [Fields](#fields)
- [Validation constraints](#validation-constraints)
- [Pi-specific behavior](#pi-specific-behavior)
- [Examples](#examples)

## Fields

| Field | Required | Purpose |
|---|---|---|
| `name` | Yes | Command and display name; used as `/skill:<name>` |
| `description` | Yes | Routing text shown to the model at startup — decides when the skill loads |
| `license` | No | License name, or path to a bundled license file |
| `compatibility` | No | Environment requirements: intended product, system packages, network access |
| `metadata` | No | Arbitrary string→string map for client-specific data |
| `allowed-tools` | No | Space-separated pre-approved tool list (experimental; support varies) |
| `disable-model-invocation` | No | `true` hides the skill from automatic model selection; `/skill:<name>` still works |

`disable-model-invocation` is a Pi-supported extra. Use it for destructive or narrowly
scoped workflows where an accidental trigger costs more than a missed one (deploy,
migration, release, "run the nightly cleanup").

## Validation constraints

`name`:

- 1–64 characters
- lowercase alphanumeric and hyphens only
- no leading, trailing, or consecutive hyphens
- must match the parent directory name (spec requirement; see below)

`description`:

- 1–1024 characters, non-empty
- describes what the skill does **and** when to use it
- contains concrete keywords an agent would see in a matching request

`compatibility`:

- 1–500 characters if present

`metadata`:

- map of string keys to string values; pick reasonably unique key names

## Pi-specific behavior

- Pi neither requires nor warns when `name` differs from the parent directory, but other
  Agent Skills implementations enforce the match. Matching names are the portable choice —
  always match them.
- Discovery locations: `~/.pi/agent/skills/`, `.pi/skills/`, `~/.agents/skills/`,
  `.agents/skills/`. Directories containing `SKILL.md` are found recursively. Project
  `.agents/skills/` is searched from the working directory through its ancestors, stopping
  at the repository root when one exists.
- Project skills load only after project trust is granted.
- The `skills` setting (`docs/settings.md`) adds extra files or directories, and supports
  glob exclusions (`!pattern`), exact inclusion (`+path`), and exact exclusion (`-path`).
- `enableSkillCommands` (default `true`) controls whether skills appear as `/skill:<name>`
  in command discovery. Manually typed `/skill:<name>` works regardless.
- Arguments after `/skill:<name>` are appended to the loaded instructions as a user
  request: `/skill:pdf-tools extract report.pdf`.
- Name collisions keep the first discovered skill and emit a warning.

## Examples

Minimal:

```yaml
---
name: pdf-tools
description: Extract text and tables from PDF files. Use when reading, converting, or inspecting PDFs.
---
```

With environment requirements and manual-only invocation:

```yaml
---
name: db-migrate
description: Apply and roll back PostgreSQL migrations for this repo. Use only via /skill:db-migrate.
compatibility: Requires psql on PATH and a DATABASE_URL environment variable. No network access needed.
disable-model-invocation: true
metadata:
  pi-skill-authoring-version: "1"
---
```

Description that triggers reliably — note the explicit cue list:

```yaml
description: Review pull requests for this repo against project conventions (naming, test coverage, changelog). Use when the user asks for a code review, PR review, or "check my changes", even if they do not mention conventions or this skill by name.
```
