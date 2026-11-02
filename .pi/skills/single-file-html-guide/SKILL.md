---
name: single-file-html-guide
description: "Create polished, self-contained single-file HTML guides, interactive documentation, process explainers, scenario explorers, runbooks, and read-only dashboards for business and technical audiences. Use when users request an offline HTML SPA, a clean navigable document with flowcharts, or an interactive guide explaining behavior under different conditions."
metadata:
  argument-hint: "Describe the topic, source material, audience, and desired output location"
---

# Single-File HTML Guide

Turn verified source material into an attractive, understandable, offline HTML
document. Combine a concise business overview with technical detail, readable
flowcharts, and scenario-based explanations where useful.

The deliverable is **one HTML file**, not a frontend project. The skill and its
starter are domain-neutral and require no other skills, libraries, or services.

## 1. Establish the document contract

Identify the requested topic, intended readers, source material, destination,
and whether the artifact is documentation, a static dashboard, or both.

- Use the user's supplied sources and preferences before asking questions.
- Ask only when missing information would materially change the content or
  implementation. Otherwise choose a sensible filename and explain the choice.
- Default to a read-only guide. Do not introduce live connections, credentials,
  configuration changes, or operational controls without an explicit request.
- Distinguish a source-derived snapshot from a live monitoring dashboard.
- For a dashboard, identify the dataset, units, time range, and freshness.
  Never invent metrics to make a page look populated.
- Preserve existing files and unrelated changes. Producing documentation does
  not authorize modifying the underlying workflow.

## 2. Establish facts before designing screens

Read the relevant code, workflow definitions, requirements, data schemas, or
operating procedures. Trace behavior rather than inferring it from names.

Build a compact internal behavior matrix:

| Dimension | Questions to settle |
|---|---|
| Entry | Who or what starts the operation? Which entries are independent? |
| Conditions | Which settings, events, or saved states select a route? |
| Actions | What is read, computed, written, sent, or deliberately skipped? |
| Persistence | What survives interruption? What does not? |
| Failure | What is fatal, partial, deferred, rejected, or recoverable? |
| Recovery | What repeats, what is reused, and what must an operator do? |
| Outcome | What changes for a business user, consumer, or downstream system? |
| Evidence | Which source supports each consequential claim? |

Important constraints:

- Do not add scheduling, retries, time-based checks, fallbacks, cleanup,
  approvals, synchronization, or recovery behavior merely because it seems
  prudent. Describe what exists; identify recommendations separately.
- A name such as "resume," "complete," or "publish" is not proof of semantics.
- Separate trigger time from saved state and configuration when they affect
  behavior differently.
- Mark unknown deployment settings and unverified external behavior explicitly.
- Do not expose secrets, private endpoints, personal data, local environment
  details, or raw operational payloads in publication-ready content.

## 3. Organize for two reading depths

Let a business reader understand purpose, outcomes, and exceptions without
reading implementation identifiers. Let a technical reader reach exact rules.

Use only the sections the topic needs. A strong default structure is:

1. **Start here:** purpose, scope, main stages, the most important distinction.
2. **Scenario explorer:** concrete situations and what actually happens.
3. **Decisions and recovery:** identity, state transitions, restart boundaries.
4. **Inside the process:** overview and focused detail flowcharts.
5. **Data and checkpoints:** stores, artifacts, inputs, outputs, and ownership.
6. **Operator playbook:** readiness, triage, next actions, and unsafe shortcuts.
7. **Reference:** parameters, glossary, limitations, and source map.

Prefer short paragraphs, meaningful headings, summary cards, decision tables,
and callouts over walls of text. Explain why a distinction matters.

Do not force a seven-section layout or a large scenario catalog onto a simple
topic. Remove irrelevant components rather than filling them with generic prose.

## 4. Apply the visual system

Use [the starter HTML](./assets/guide-template.html) when helpful. It is a
generic demonstration, not factual content or a mandatory final layout.
Copy it to the requested destination and replace its example content completely.
The delivered HTML must not depend on files inside the skill package.

Default visual direction:

- Pale neutral page background, white cards, dark slate text, one muted accent.
- Sticky left navigation on wide screens; compact scrollable navigation on
  narrow screens. Show the current section without relying on color alone.
- Spacious layout, restrained borders, moderate rounded corners, no unnecessary
  gradients, decorative charts, animation, or ornamental icons.
- System fonts only. Body text about 15-16 px, headings 28-48 px, comfortable
  line height around 1.5-1.6.
- Use a small set of CSS variables for colors, spacing, and radii.
- Constrain long prose widths. Collapse multi-column content on small screens.
- Keep dense tables and diagrams scrollable inside their containers; avoid
  document-wide horizontal overflow.
- Never shrink diagram labels to make an oversized chart fit the screen.

Use precise labels such as "Source snapshot" or "Example dataset" rather than
live-looking status badges without live evidence.

## 5. Design scenario explanations

Include scenarios when the same apparent action can produce different results.
Cover meaningful branches from the source, not a predetermined number.

Each scenario should explain:

1. Entry event or initiating action.
2. Relevant prior state and assumptions.
3. Decision or identity selection.
4. Work performed, skipped, retried, or reused at each stage.
5. Expected success, partial, failure, or waiting outcome.
6. Business or downstream impact.
7. Recommended operator action and important caution.
8. Behavior on the next attempt, if applicable.

Implement a searchable, optionally category-filtered selector with readable
details. Keep scenario content in one embedded data structure and reuse it for
the screen and print versions.

- Provide a useful empty-search state and result count.
- Keep selected state and scenario links consistent.
- Do not reset the selector to its beginning after every choice.
- Avoid involuntary scrolling or focus jumps while typing a search.
- Do not represent blocked or skipped stages as actions that actually ran.
- Never present invented timing differences as distinct code paths.
- Replace generic demo scenarios with verified topic-specific situations.

## 6. Draw flowcharts that explain behavior

Use inline SVG with selectable text as the default. Do not load a diagram
renderer from a CDN. If an existing renderer is appropriate, its output must
still be embedded and visually inspected.

Conventions:

| Meaning | Treatment |
|---|---|
| Trigger | Capsule naming event, conditions, and operation started |
| Automated action | White rectangle with thin dark outline |
| Human action | Muted slate rectangle with high-contrast white text |
| Decision | Diamond with labeled outgoing branches |
| Subprocess | Rectangle with double vertical side lines |
| Outcome | Rounded rectangle naming a specific result |
| Supporting detail | Adjacent annotation, not an extra action |

Include a compact legend for the conventions actually used.

- Explain every real entry point independently. Alternative triggers do not
  imply parallel work or synchronization.
- Keep the main path top-to-bottom. Use adjacent columns for alternatives.
- Prefer orthogonal connectors with arrowheads at destination boundaries.
- Avoid lines through unrelated shapes, ambiguous crossings, unattached
  arrowheads, and labels overlapping nodes.
- Keep text to two to four short lines per action. Start around 16 px for node
  labels and 14 px for annotations.
- Split dense behavior into an overview and named detail charts.
- Preserve meaningful waits, loops, writes, rejection, and failure paths.
- Give each SVG a descriptive title and text alternative. Explain deliberate
  simplifications outside the diagram.

## 7. Implement one portable file

Embed CSS, JavaScript, SVG, scenario data, and any required small assets.

- No package installation, build step, backend, fetch calls, CDN assets,
  remote fonts, analytics, or service workers for an offline guide.
- Work when opened directly with `file://`; use a classic inline script rather
  than imports or external module loading.
- Use semantic headings, landmarks, labeled inputs, real buttons, visible focus,
  adequate contrast, and keyboard-operable controls.
- Use a small, explicit hash router if needed. Validate routes; support direct
  links, browser Back/Forward, sensible scroll behavior, and active navigation.
- Insert variable content with DOM APIs and `textContent`, not unsanitized
  `innerHTML`. Treat source text as data, not executable markup.
- Leave useful static content and a clear notice if JavaScript is unavailable.
- A copy-link button must disclose that local file links require the same path
  to be accessible. Handle unavailable clipboard APIs with visible feedback.
- Respect reduced-motion preferences. Avoid persistent browser storage unless
  the task genuinely needs it.
- Include print styling: all sections and scenarios should be available,
  interactive chrome hidden, expanded reference details readable, diagrams
  contained, and text unclipped. Printing only the selected scenario is not a
  substitute for a complete guide.
- Relative source links are optional conveniences, not runtime dependencies.
  Explain that they may not resolve if the HTML is moved independently.

Keep the implementation inspectable. Do not introduce a framework merely to
render navigation, a handful of diagrams, and a filtered list.

## 8. Verify content and rendering

Run the lightest available checks that directly cover the artifact.

### Behavioral and structural checks

- Confirm schedules, state rules, parameters, outcomes, and recovery claims
  agree with the source.
- Check HTML identifiers, internal routes, source links, and script syntax.
- Check for console errors, external requests, and leftover demo content.
- Exercise every route and scenario; test search, categories, empty results,
  direct links, Back/Forward, and clipboard fallback where implemented.
- Verify scenario and print counts agree with the actual dataset.
- Test print media: all sections/scenarios visible, details expanded, control
  panels hidden. Restore screen state afterwards.

### Visual checks

Render in an available browser and inspect desktop and narrow/mobile layouts.
Inspect the diagrams themselves, not just JavaScript syntax.

- Check node text bounds, label placement, connectors, arrowheads, and legends.
- Check long headings, tables, sticky navigation, selector scroll position, and
  container overflow at normal reading size.
- Confirm mobile layouts do not create document-wide horizontal scrolling.
- Inspect an ordinary scenario and an exceptional/recovery scenario.
- Check that unverified data is not styled as confirmed live status.

If browser tooling is unavailable, perform structural checks and explicitly
state that visual verification remains pending. Do not claim inspection,
accessibility compliance, or operational validation that was not performed.

## 9. Deliver and maintain

Link the saved HTML and briefly describe its main sections and interactions.
State verification performed and important limitations. Do not create unrelated
reports, screenshots, PDFs, or extra source files unless requested.

When updating an existing guide, trace changed behavior through prose,
flowcharts, scenarios, parameter tables, FAQs, and print content. Remove stale
claims rather than appending contradictory notes.

For publication of this skill, distribute this directory as-is: generic
instructions and a generic starter, with relative resource links only. Keep
private source material, generated project guides, credentials, machine paths,
and session history out of the skill package.
