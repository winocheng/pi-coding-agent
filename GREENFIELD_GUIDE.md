# Starting a New Project from Scratch with OpenSpec

OpenSpec is most often used for brownfield work — changing a system that already exists.
But it works for a brand-new project too, as long as you give the empty repo direction
before you start writing code.

This guide documents the **umbrella-roadmap pattern** described in the article
[OpenSpec is built for brownfield — I used it to build from nothing](https://dev.to/shyamala_u/openspec-is-built-for-brownfield-i-used-it-to-build-from-nothing-18jm)
by Shyamala U. The author used it to build a complete offline Windows desktop inspection app
(Wails + Go + Svelte + SQLite) from an empty folder.

---

## The core idea

For a new project, you start with one big OpenSpec change — the **umbrella** — that describes
the **entire MVP**. Its `tasks.md` is not an implementation checklist; it's a list of *child
changes to create*. Each child change is a self-contained proposal you review and apply
independently.

```text
umbrella change (roadmap)
├── task 1: create child change `initialize-app-foundation`
├── task 2: create child change `create-resumable-draft`
├── task 3: create child change `attach-photos-to-questions`
├── task 4: create child change `complete-report-export`
└── task 5: create child change `package-desktop-build`
        │
        ▼  (when you apply a task, it spawns a child change)

openspec/changes/initialize-app-foundation/
├── proposal.md      ← why this scaffolding
├── specs/           ← what the foundation must support
├── design.md        ← chosen tech, alternatives, risks
└── tasks.md         ← actual implementation steps (go + npm commands)
```

The umbrella says **what the MVP needs**. Each child change says **how one piece will be
built and verified**.

---

## The loop, step by step

### Step 1 — Create the umbrella roadmap

Tell the agent what the MVP is. Ask for an umbrella change:

```text
You: /opsx-propose my-app-mvp

You: This is an umbrella change acting as a roadmap.
     Tasks should be a list of child changes to create, not implementation steps.
     Group them logically:
       - scaffolding
       - core workflow
       - evidence / export
       - packaging
     The MVP is [describe your product in one paragraph].
```

The agent creates `openspec/changes/my-app-mvp/` with a roadmap as `tasks.md`.

**Stop. Read `tasks.md`.** Rearrange the order. Delete the tasks you do not need. Add what
you missed. This plan is yours: it should reflect your judgement, not the agent's first draft.

### Step 2 — Work through one task at a time

Pick the first task (say, `initialize-app-foundation`). Propose the child change:

```text
You: /opsx-propose initialize-app-foundation

You: This is the first task from the umbrella change `my-app-mvp`.
     Set up the project scaffolding:
       - [tech stack and structure you decided]
       - database schema
       - basic build pipeline
     The umbrella roadmap is at openspec/changes/my-app-mvp/tasks.md.
```

The agent creates `openspec/changes/initialize-app-foundation/` with its own proposal,
specs, design, and tasks. **Review it.** Then:

```text
You: /opsx-apply
```

The agent implements. You test. Commit.

### Step 3 — Repeat, adjusting as you learn

Each subsequent child change benefits from what the previous one revealed:

```text
You: /opsx-propose create-resumable-draft

You: Now that the app exists, this change adds draft save/resume.
     During scaffolding I learned [something that affects this feature].
```

The umbrella roadmap is a **guide, not a contract**. Update it when the real work teaches you
something. The article author changed the roadmap after writing it. They replaced DOCX export with
PDF. They split up a vessel/draft flow. They narrowed a findings workflow.

### Step 4 — Archive as you go

After each child change is done and tested:

```text
You: /opsx-archive
```

Archived changes go to `openspec/changes/archive/<date>-<name>/`. Their spec deltas
merge into `openspec/specs/`. The umbrella stays open until the MVP is done; then you
archive it too.

One catch: archiving does **not** tick the child off the umbrella roadmap. It does not refresh
any counts either. No CLI command does either job. See
[Archive bookkeeping the CLI will not do for you](#archive-bookkeeping-the-cli-will-not-do-for-you)
before you archive your first child.

---

## Concrete example: a todo app from scratch

Umbrella proposal:

```text
You: /opsx-propose todo-app-mvp
     Umbrella change. Roadmap of child changes:
       1. initialize-nextjs-project   — Next.js, Prisma, SQLite, basic layout
       2. create-todo-model           — schema, CRUD, API routes
       3. build-todo-list-ui          — list, add, delete, checkbox toggle
       4. add-filters-and-search      — status filter, text search
       5. add-edit-todo-detail        — inline edit, due dates, priorities
       6. package-and-deploy          — Dockerfile, deploy instructions
```

Then one at a time:

```text
You: /opsx-propose initialize-nextjs-project
You: /opsx-apply
You: (test it, commit, maybe adjust the roadmap)
You: /opsx-propose create-todo-model
You: /opsx-apply
...
```

---

## Archive bookkeeping the CLI will not do for you

Adopting the pattern on a real from-nothing project exposed one gap. `/opsx-archive` moves
`changeRoot` into `archive/` and merges spec deltas. That is all it does. Nothing in the
archive path:

- ticks the archived child's line in the umbrella's `tasks.md`,
- or refreshes the "N capabilities / M delivered" counts that README and guide files assert.

So the roadmap drifts. In the first round of that project, two children archived while the
umbrella still read `1/18`. Three counts went false within minutes of the next archive. Make
the bookkeeping part of the workflow. Do not leave it as a rule in a document, which only
binds if someone opens it.

### Put it in `config.yaml`, not in the generated files

Three places could hold the duty, and they fail differently:

| Channel | Takes effect | Survives `openspec update` |
|---|---|---|
| `openspec/config.yaml` → `operations.<op>.guidance` | next run | **yes** |
| hand-editing `.pi/skills/openspec-*/SKILL.md` / `.pi/prompts/opsx-*.md` | immediately | **no — reverted** |
| `AGENTS.md` prose | only if the agent reads it | yes, but unenforced |

Use the config channel. It is a first-class key, not a workaround. It also rides a code path the
bundled workflow already walks. Step 4 of `openspec-archive-change/SKILL.md` runs
`openspec instructions archive --change "<name>" --json`. The workflow is told to treat the returned
`operationGuidance` as additive advice. So the guidance arrives without any edit.

Measured on OpenSpec 1.14.0 (verified in a scratch root, then re-verified in this repo):

- `operations` is in the config schema; supported operation ids are exactly `apply` and
  `archive`. An unknown id prints `Unknown operation ID ... Supported operation IDs: apply,
  archive`, skips it, and still exits 0.
- `openspec update` rewrites only the tool's skill and command files. A `config.yaml` holding
  a custom `operations` block came through byte-identical (md5 unchanged).
- The next `openspec update` **reverted a hand edit** to the generated archive `SKILL.md` back to
  pristine: its md5 matched the freshly-initialised file, with 0 occurrences of the edit. The config
  guidance still reached the workflow. Treat the generated files as disposable.

### Paste this into a new project's `openspec/config.yaml`

Append it at **end of file**. Do not splice it in where the commented-out example block sits. That
example literally contains the text `operations:`. A search-and-insert that targets it cuts the file
mid-comment.

```yaml
operations:
  archive:
    guidance:
      - >-
        If the change being archived is a child of an umbrella roadmap change, tick that
        child's line in the umbrella's tasks.md. Tick it at archive time, not at
        implementation time. No CLI step does this: the archive move touches nothing
        outside changeRoot.
      - >-
        Commit the bookkeeping edits in the same commit as the archive move, then state in
        the summary that they were committed. If they could not be done, say so rather
        implying the roadmap is current.
      - >-
        Refresh every count or status claim that the archive makes stale (README, guides,
        estimation notes). Find them by searching for their wording rather than recalling
        it, and take the replacement numbers from `openspec list --json`,
        `ls openspec/specs/`, and `ls openspec/changes/archive/` rather than from memory.
  apply:
    guidance:
      - >-
        Document a command only after actually running it. Never report a passing test,
        lint, or CI run that was not observed.
      - >-
        When a task implements one slice of an umbrella roadmap, keep the change scoped to
        that slice; anything learned that changes the roadmap belongs in an
        `/opsx-update` of the umbrella, not in silent scope drift.
```

**Use a folded scalar (`>-`) for every entry.** A bare list item that contains `colon space` parses
as a *mapping*, not a string. The example is
`- Never report a passing CI run: this repo has no CI`. The CLI then prints `Guidance for operation 'archive' must be an array of strings, ignoring this operation's guidance`. It drops **all** of that
operation's guidance and still exits 0. A silently ignored rule is worse than a loud failure. Check
the parse:

```bash
python3 -c "import yaml;d=yaml.safe_load(open('openspec/config.yaml'));\
print([type(x).__name__ for x in d['operations']['archive']['guidance']])"
# ['str', 'str', 'str']   <- anything containing 'dict' is a broken entry
```

### Confirm the guidance actually reaches the workflow

```bash
openspec instructions archive --change <some-open-change> --json \
  | python3 -c "import json,sys;print(json.load(sys.stdin).get('operationGuidance'))"
```

Expect your entries echoed back. If the key is missing, the block did not parse.

### Does this interfere with the bundled commands?

No. This is the part worth re-verifying after any upgrade:

- Nothing under `.pi/` was edited. The generated skills and prompts stay byte-identical to a
  fresh `openspec init`. So an upgrade cannot conflict with them, and `openspec update` has
  nothing to revert.
- The workflow is *advisory by design*. If the lookup fails or returns nothing, the archive skill
  continues with "no context and no operation guidance". It does not stop. A malformed block
  degrades to a warning, never a blocked archive.
- `context` is the only required-prompt field; `operationGuidance` is explicitly additive, so
  adding entries cannot override the bundled steps.
- Every bundled command was re-run after adding the block: `list --json`, `validate --all`,
  `doctor`, `context` all exit 0 with no warnings on stderr.

This repo carries the block in `openspec/config.yaml` as the reference copy. Its `archive` entries
are written conditionally: "if the change being archived is a child of an umbrella". So they stay
inert here, because this repo has no umbrella change yet. They are correct as soon as you copy the
file into a greenfield project.

---

## What the article author did differently

Two things to know from the source article:

### Custom `--task` selector

The author extended `/opsx-apply` with a `--task` flag. It implements only one task from the
umbrella at a time, *without* spawning a child change. Your default OpenSpec install does not need
this. Run `/opsx-propose` once per child change. You get the same "one bite at a time" effect, and
the review step is explicit rather than a flag.

### `AGENTS.md` alongside OpenSpec

OpenSpec defines **what each change should do**. `AGENTS.md` defines **project-wide
engineering rules** — things that should apply to every change regardless of scope. The author kept the
two separate, and recommends the same. Useful things to put in `AGENTS.md`:

- "Every bug fix includes a regression test that reproduces the faulty behaviour."
- "Frontend follows the design system in `docs/design-system.md`."
- "Test observable behaviour, not implementation details."
- "Never commit a change that breaks the existing test suite."

Split it this way. OpenSpec covers product changes. `AGENTS.md` covers engineering standards.
Role-specific subagent instructions (for example "frontend agent must follow the design system")
go in their own prompt files.

---

## The mental model

| Layer | What it defines | Where it lives |
|-------|----------------|----------------|
| Umbrella change | What the MVP needs (roadmap) | `openspec/changes/<umbrella>/tasks.md` |
| Child changes | How one feature gets built | `openspec/changes/<feature>/{proposal,specs,design,tasks}.md` |
| `AGENTS.md` | Project-wide engineering rules | repo root |
| `operations.*.guidance` | The same duties, injected into every apply/archive run | `openspec/config.yaml` |
| Archived changes | What was built and why | `openspec/changes/archive/` |
| `openspec/specs/` | Current system behaviour (the truth) | merged from archived deltas |

The specs don't predict everything up front. They give each agent session the same
reviewed starting point, keep changes small, and preserve *why* the design evolved. That's
what lets you pause for weeks, switch models, or revisit a feature without rebuilding the
plan from memory.

---

## What to expect in practice

- **More tokens per session.** Every agent reads specs + code + change history. This raises
  cost and eats rate limits. The article author matched model to task — strong model for
  design, cheap model for admin — to stay under the cap.
- **The roadmap will change.** That's the point. Update the umbrella tasks as you learn.
- **Bugs will still happen.** Specs reduce ambiguity; they don't replace running the app
  and looking at the output.
- **One task at a time, not one giant change.** The whole pattern exists to keep the agent's
  context window tight and each review tractable.

---

## Try it right now

In this repo, from a Pi session:

```text
You: /opsx-propose hello-world-mvp
     Umbrella change. Roadmap of child changes:
       1. write-a-hello-world-file — create a hello.md with a greeting
       2. link-it-from-the-readme  — add a reference in README.md
```

Then run `/opsx-apply` on the umbrella. Or run `/opsx-propose write-a-hello-world-file` for one
child change, then `/opsx-apply` that. Either way, you have run the pattern on a repo that already
has OpenSpec configured.

---

*Source: Shyamala U, [OpenSpec is built for brownfield — I used it to build from nothing](https://dev.to/shyamala_u/openspec-is-built-for-brownfield-i-used-it-to-build-from-nothing-18jm), dev.to.*

*Last updated: 2026-10-28 — the prose was simplified under the `asd-ste100` skill
(ASD-STE100-inspired). Long sentences were split and passive constructions rewritten. No command,
path, version, flag, code block, table row, or claim was changed. The original date was 2026-10-01.*

*Earlier: 2026-10-01 — first version.*
