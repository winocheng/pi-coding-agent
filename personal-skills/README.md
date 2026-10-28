# Personal Skills

These skills belong to **your machine**, not to one project. Pi loads personal skills from
`~/.pi/agent/skills/` in every session, so they follow you into whatever repo you open. That is right
for general workflows such as UI inspection. It is wrong for repo-specific work; those skills live in
[`.pi/skills/`](../.pi/skills).

This directory keeps those skills under version control instead of only in a home folder. Pi does
**not** discover skills from here. That is deliberate: the tracked copy cannot then collide with a
project skill of the same name.

## Install

Link each skill into the personal skills directory. The repo then stays the single source of truth, so
an edit takes effect at once with no copy or sync step.

```bash
mkdir -p ~/.pi/agent/skills
ln -s "$PWD/personal-skills/<name>" ~/.pi/agent/skills/<name>
```

Check that Pi sees the skill. Its name should appear in the skills list at startup, with no collision
warning:

```bash
pi -p "List the exact names of every Agent Skill you currently have available, names only."
```

Pi's loader follows symlinked skill directories. Scripts keep their executable bit, and relative
`references/` and `scripts/` paths resolve normally.

To undo, remove the link: `rm ~/.pi/agent/skills/<name>`. This removes the link, not the files.

## Contents

| Skill | Purpose |
|---|---|
| [frontend-visual-loop](frontend-visual-loop/SKILL.md) | Renders UI with `agent-browser` and returns screenshots to the model as real images while it fixes frontends. See [step 13 of the configuration guide](../CONFIGURATION_GUIDE.md#13-frontend-visual-loop-browser-screenshots-the-model-can-see) |
