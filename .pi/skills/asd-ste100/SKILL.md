---
name: asd-ste100
description: Write or rewrite human-facing documentation in clear, simple English. Short sentences, active voice, one instruction per step, and preserved facts and literals. Use when creating or editing a README, changelog, setup guide, tutorial, release note, or user guide, or when asked to simplify technical prose.
license: MIT
---

# ASD-STE100-inspired writing

Use this skill to write documentation that a person can follow quickly.

It is inspired by ASD-STE100, the simplified technical English specification maintained
by the Aerospace and Defense Industries Association of Europe. The guidance here is
original. It is not a copy of the standard, and it is not certified against it.

What this skill does not do:

- It does not bundle the official ASD-STE100 dictionary.
- It does not check whether a word is approved.
- It does not verify full compliance with the standard.
- Short sentences and passing tests are not proof of compliance.

Say "ASD-STE100-inspired" when you describe the result. Never claim certified
compliance.

Inspiration: https://github.com/danyuchn/asd-ste100-skill

## Pick the mode for each section

Choose the mode per section, not per file. One document can hold both.

| Section type | Mode | Target sentence length |
|---|---|---|
| Steps, setup, commands, configuration, procedures | strict | 20 words maximum |
| Introductions, overviews, rationale, background | lighter | 25 words maximum |

Procedural text tells a reader what to do. Explanatory prose tells a reader what
something is or why it exists.

When a paragraph mixes both, split it. Put the instruction in the procedural section
and the reason in the explanatory one.

## Write procedural text

Follow every rule below in strict mode.

1. Put one instruction in each sentence.
2. Keep each sentence to 20 words or fewer.
3. Start with the action verb: "Run the command", not "The command should be run".
4. Name the actor. Do not hide who acts.
5. Use active voice. Rewrite passive constructions.
6. Use one term for one thing. Do not alternate synonyms.
7. Number ordered steps. Keep each step one action.
8. Put the condition before the instruction when the step is conditional.
9. State the result after the step, when the reader needs it.
10. Write command lines exactly as the reader must type them.
11. Separate "required" from "optional". Do not imply a choice that is not there.
12. Do not chain steps with "and then". One step per sentence.

Useful verbs: run, open, set, add, remove, replace, check, install, start, stop.

Avoid in strict mode: "should be able to", "it is possible to", "in order to",
"utilize", "perform a configuration of", and any phrase that hides the actor.

## Write explanatory prose

Follow these rules in lighter mode.

1. Keep each sentence to 25 words or fewer.
2. Lead each paragraph with its main point.
3. Prefer common words over rare ones.
4. Explain a term the first time the document uses it.
5. Keep one idea per paragraph.
6. Use active voice unless the actor truly does not matter.

## Preserve meaning while you simplify

Brevity never justifies a wrong statement. Keep all of the following:

- **Facts.** Numbers, names, versions, and settings stay as they are.
- **Conditions.** If a statement holds only under a condition, keep the condition.
- **Sequence.** Do not reorder steps unless the new order is proven equivalent.
- **Negation.** Keep every "not", "never", and "no".
- **Uncertainty.** Keep "may", "might", "can", "usually", and "in some cases".
- **Obligation strength.** Keep the difference between optional, recommended, and
  required.
- **Exceptions.** Do not drop an exception to shorten a sentence.

Two rules override all others:

- "may" never becomes "will". A possibility never becomes a guarantee.
- A conditional prohibition never becomes unconditional. Keep the "if" clause.

When a sentence must be longer than the target to stay accurate, keep it. Then note the
exception below the section:

```text
Kept as-is: <sentence> — <one-line reason>
```

Do not delete content to meet a word count. Do not merge two distinct statements into
one sentence.

## Protect technical literals

Preserve these exactly, unless the task asks you to change them:

- Code blocks and their content.
- Inline code spans.
- Command syntax, flags, and argument order.
- URLs and paths.
- File names, identifiers, API names, and version numbers.
- Heading levels and document structure.
- Tables, lists, and link targets.

Simplify the prose around a literal. Never simplify the literal itself.

A human-facing document is not exempt from this skill just because it contains code.

## Check vocabulary as advice, not as a gate

Prefer a common word when it carries the same meaning. Use one word for one concept.

This check is advisory. This skill bundles no list of approved words, because the
official dictionary is not redistributed here. Do not report a word as "approved" or
"not approved". You cannot verify that, and a claim you cannot verify is worse than no
claim.

When a term is necessary and unusual, define it in the document instead of replacing it.

## Output shape for rewrite-only work

When the task is only "rewrite this", return the rewritten text.

- No preamble. Do not announce the mode or the skill.
- No introduction. Do not restate what the document is about.
- No change summary. Do not list your edits.
- No closing offer to help further.

Two additions are allowed:

1. A `Kept as-is:` note for a necessary exception.
2. An explanation or comparison, but only when the task asks for one.

When the task asks for both a rewrite and an explanation, give the rewrite first, then
the explanation.

## Examples

### Example 1: a setup procedure

Before:

```markdown
It should be noted that in order for the package `pi-asd-ste100` to be utilized by the
agent, the command `pi install npm:pi-asd-ste100` needs to be run by the user, and
afterwards it will be necessary to restart the session so that the newly installed
extension can be loaded properly.
```

After:

```markdown
1. Run `pi install npm:pi-asd-ste100` to install `pi-asd-ste100`.
2. Restart the session.

The restart loads the new extension.
```

Rule shown: one instruction per sentence, active voice, actor named, and both inline
literals preserved exactly.

### Example 2: an overview paragraph

Before:

```markdown
This package is intended to provide a set of comprehensive writing guidelines which
are utilized in an adaptive manner depending upon the particular type of content that
is being produced by the agent at any given moment during operation.
```

After:

```markdown
This package guides the writing of human-facing documents.

It applies two modes. Procedures get strict rules. Explanatory prose gets lighter
rules. The mode is chosen per section.
```

Rule shown: short sentences, one idea per paragraph, and no loss of the original claim.

### Example 3: a qualified statement

Before:

```markdown
The rewrite step may fail when the source message was produced under a different
model, in which case users are strongly advised to consider performing a manual copy
of the original text, though this is not always necessary.
```

After:

```markdown
The rewrite step may fail when the source message came from a different model.

When that happens, copy the original text by hand. This step is not always needed.
```

Rules shown: the uncertainty "may" stays, the condition stays, the negation stays, and
obligation strength stays advisory rather than becoming a requirement.

## When you are done

Check these four items:

1. Every number, command, path, and link is byte-identical to the source.
2. Every condition, negation, and qualifier survived.
3. Procedural sentences meet the 20-word target, or the exception is noted.
4. The text says "ASD-STE100-inspired" and claims no certified compliance.

If a check fails, fix the text. Do not shorten a correct sentence to satisfy a count.
