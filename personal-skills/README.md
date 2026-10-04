# Personal Skills

Skills that belong to **your machine**, not to a project. Pi loads personal skills from
`~/.pi/agent/skills/` in every session, so they follow you into whatever repo you open — which is
what you want for general workflows like UI inspection, and wrong for repo-specific ones (those live
in [`.pi/skills/`](../.pi/skills)).

This directory exists so those skills are version-controlled instead of living only in a home
folder. Pi does **not** discover skills from here, which is deliberate: it keeps the tracked copy
from colliding with a project skill of the same name.

## Install

Each skill is symlinked into the personal skills directory, so this repo stays the single source of
truth and edits take effect immediately with no copy or sync step:

```bash
mkdir -p ~/.pi/agent/skills
ln -s "$PWD/personal-skills/<name>" ~/.pi/agent/skills/<name>
```

Verify Pi sees it — the name should appear in the skills list at startup, with no collision warning:

```bash
pi -p "List the exact names of every Agent Skill you currently have available, names only."
```

Pi's loader follows symlinked skill directories, so scripts keep their executable bit and relative
`references/` and `scripts/` paths resolve normally.

To undo: `rm ~/.pi/agent/skills/<name>` (removes the link, not the files).

## Contents

| Skill | Purpose |
|---|---|
| [frontend-visual-loop](frontend-visual-loop/SKILL.md) | Renders UI with `agent-browser` and feeds screenshots back to the model as real images while fixing frontends. See [step 12 of the configuration guide](../CONFIGURATION_GUIDE.md#12-frontend-visual-loop-browser-screenshots-the-model-can-see) |
