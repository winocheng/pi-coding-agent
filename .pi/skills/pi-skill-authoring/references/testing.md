# Testing and Iterating on Skills

A skill is only useful if it (a) loads, (b) triggers on the right requests, and (c) changes
Pi's behavior for the better. Test all three.

## Table of contents

- [Quick smoke test](#quick-smoke-test)
- [Behavior test cases](#behavior-test-cases)
- [Trigger evaluation](#trigger-evaluation)
- [The iteration loop](#the-iteration-loop)
- [Reviewing with the user](#reviewing-with-the-user)

## Quick smoke test

1. `python3 <pi-skill-authoring-dir>/scripts/validate_skill.py <skill-dir>` — catches
   frontmatter, naming, size, and broken-reference problems without starting Pi.
2. In a Pi session rooted where the skill is discoverable, run `/reload` and read startup
   diagnostics. Warnings name the file and field.
3. Type `/skill:` and confirm the skill appears in command discovery (it will not if
   `enableSkillCommands` is false or `disable-model-invocation` is true — typed commands
   still work).
4. Invoke `/skill:<name> do something small` and confirm the instructions loaded are the
   ones you wrote.

If the skill does not appear at all: check that the directory contains `SKILL.md`, that
`description` is present and non-empty, that the YAML parses, and that you are running Pi
from a location where the skill directory is discoverable (project skills also require
project trust).

## Behavior test cases

Write 2–3 prompts a real user would actually type — concrete, with file paths, casual
phrasing, maybe a typo. Bad: "Format this data". Good: "ok the sales csv is in ./data,
called something like q4-final-v2.csv, can you add a margin % column? revenue is C, costs
are D i think".

For each, note the expected end state before running. Then run the task with the skill
available and observe:

- Did Pi load the skill, or solve it without?
- Did it follow the workflow, or drift?
- Did it waste turns on steps the skill told it to do that were not useful?
- Did it write a helper script that the skill should have bundled?

Read the transcript, not just the final output. Wasted work shows up in the middle.

Keep the cases in the skill directory as `evals/evals.json` when the user wants a repeatable
set:

```json
{
  "skill_name": "example-skill",
  "evals": [
    { "id": 1, "prompt": "user's task prompt", "expected_output": "description of result", "files": [] }
  ]
}
```

Skills with objectively verifiable output (file transforms, extraction, code generation,
fixed workflows) benefit from test cases. Subjective ones (writing style, design) are
better judged by a human reading the result — do not force assertions onto them.

If subagents or parallel runs are available, run each case with the skill and without it
(baseline) in the same batch, so you can tell whether the skill is actually responsible for
the difference. Otherwise, run the cases yourself one at a time and lean on user review.

## Trigger evaluation

The `description` field is the trigger mechanism, so test it separately from the body.

Build ~20 realistic queries:

- **8–10 should-trigger**: varied phrasings of the same intent, formal and casual, plus
  cases where the user never names the skill or file type but clearly needs it, and cases
  where this skill competes with another and should win.
- **8–10 should-not-trigger**: the valuable ones are *near-misses* that share keywords but
  need something else. "Write a fibonacci function" as a negative for a PDF skill tests
  nothing.

```json
[
  { "query": "the user prompt", "should_trigger": true },
  { "query": "another prompt", "should_trigger": false }
]
```

Let the user review and edit the set before you use it — bad queries produce bad
descriptions. Then check each query against the description and revise the description
until the split is right. Prefer adding concrete cue phrases ("Use when the user mentions
X, Y, or Z, even if they do not say 'skill'") over making the description longer and
vaguer. Stay under 1024 characters.

One thing to know: models mainly consult skills for tasks they cannot trivially handle
alone. A one-step request like "read this PDF" may not trigger even with a perfect
description. Make trigger queries substantive enough that consulting a skill helps.

## The iteration loop

1. Apply improvements to the skill.
2. Re-run the test cases; keep prior outputs so you can compare (a sibling
   `<skill-name>-workspace/iteration-N/` directory works well).
3. Review with the user.
4. Repeat until the user is happy, feedback is empty, or progress stalls.

When improving:

- **Generalize, do not patch.** You are iterating on a few examples so you can move fast,
  but the skill will be used on prompts nobody has seen. Fix the underlying instruction,
  not the example.
- **Keep it lean.** Delete instructions that did not change any outcome.
- **Explain the why.** If feedback is terse or frustrated, infer the real goal and encode
  that understanding, rather than adding another rigid rule.
- **Bundle repeated work.** If every run wrote the same helper, put it in `scripts/` once
  and point the skill at it.

Write a draft, then re-read it with fresh eyes before showing the user. Most skills improve
more from one careful editing pass than from another feature.

## Reviewing with the user

Present results compactly: for each test case, the prompt, what Pi did differently with the
skill, and the output (or its path, if it is a file). Ask "How does this look? Anything
you'd change?" and treat empty feedback as approval. If a diff is useful, open it with the
`vscode` skill or `code -d <old> <new>`.
