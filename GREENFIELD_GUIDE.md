# Starting a New Project from Scratch with OpenSpec

OpenSpec is most often used for brownfield work — changing a system that already exists.
But it works just as well for a brand-new project, as long as you give the empty repo
direction before you start writing code.

This guide documents the **umbrella-roadmap pattern** described in the article
[OpenSpec is built for brownfield — I used it to build from nothing](https://dev.to/shyamala_u/openspec-is-built-for-brownfield-i-used-it-to-build-from-nothing-18jm)
by Shyamala U. It was used to build a complete offline Windows desktop inspection app
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

Tell the agent what the MVP is and ask for an umbrella change:

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

**Stop. Read `tasks.md`.** Rearrange the order, delete things you don't need, add things
you missed. This is your living plan — it should reflect your judgement, not the agent's
first draft.

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

The umbrella roadmap is a **guide, not a contract**. Update it when the real work
teaches you something. The article author replaced DOCX export with PDF, split up a
vessel/draft flow, and narrowed a findings workflow — all after the roadmap was written.

### Step 4 — Archive as you go

After each child change is done and tested:

```text
You: /opsx-archive
```

Archived changes go to `openspec/changes/archive/<date>-<name>/`. Their spec deltas
merge into `openspec/specs/`. The umbrella stays open until the MVP is done; then you
archive it too.

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

## What the article author did differently

Two things to know from the source article:

### Custom `--task` selector

The author extended `/opsx-apply` with a `--task` flag so it would implement only one task
from the umbrella at a time — *without* spawning a child change. Your default OpenSpec
install doesn't need this: using `/opsx-propose` per child change gives you the same
"one bite at a time" effect, and the review step is explicit rather than a flag.

### `AGENTS.md` alongside OpenSpec

OpenSpec defines **what each change should do**. `AGENTS.md` defines **project-wide
engineering rules** — things that should apply to every change regardless of scope. The
author kept these separate and recommended the same. Useful things to put in `AGENTS.md`:

- "Every bug fix includes a regression test that reproduces the faulty behaviour."
- "Frontend follows the design system in `docs/design-system.md`."
- "Test observable behaviour, not implementation details."
- "Never commit a change that breaks the existing test suite."

Split: OpenSpec = product changes; `AGENTS.md` = engineering standards; role-specific
subagent instructions (e.g. "frontend agent must follow the design system") go in their
own prompt files.

---

## The mental model

| Layer | What it defines | Where it lives |
|-------|----------------|----------------|
| Umbrella change | What the MVP needs (roadmap) | `openspec/changes/<umbrella>/tasks.md` |
| Child changes | How one feature gets built | `openspec/changes/<feature>/{proposal,specs,design,tasks}.md` |
| `AGENTS.md` | Project-wide engineering rules | repo root |
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

Then `/opsx-apply` the umbrella, or `/opsx-propose write-a-hello-world-file` for one
child change and `/opsx-apply` that. Either way, you've run the pattern on a repo that
already has OpenSpec configured.

---

*Source: Shyamala U, [OpenSpec is built for brownfield — I used it to build from nothing](https://dev.to/shyamala_u/openspec-is-built-for-brownfield-i-used-it-to-build-from-nothing-18jm), dev.to.*

*Last updated: 2026-10-01*
