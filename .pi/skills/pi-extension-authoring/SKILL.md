---
name: pi-extension-authoring
description: Design, write, debug, and package TypeScript extensions for the Pi coding agent. Use whenever the user wants to create an extension, add a custom tool or slash command to Pi, hook lifecycle events (tool_call, before_agent_start, session_start), block or confirm dangerous operations, register a model provider or MCP server, build custom terminal UI, persist session state, or troubleshoot an extension that fails to load. Trigger even when the user does not say "extension" but asks for executable Pi behavior ("add a /deploy command", "make pi ask before rm -rf", "give the model a tool that queries our API").
---

# Pi Extension Authoring

Extensions are TypeScript modules that add executable behavior to Pi: tools, commands,
event handlers, providers, session state, terminal UI. An extension runs **inside the Pi
process with full OS permissions** and can inspect prompts, tool calls, files, credentials,
and session history — so it is trusted code, and only trusted sources should be loaded.

If the user only needs reusable instructions, that is a skill (`/skill:pi-skill-authoring`),
not an extension. Extensions are for behavior Pi cannot do from instructions alone.

Figure out where the user is — new extension, existing one to modify, or one that fails to
load — and join them there.

## Step 1: Capture intent

Extract what you can from the conversation, then confirm the gaps:

1. What should the extension do, and who triggers it — the model (tool), the user
   (command/shortcut/flag), or Pi itself (event)?
2. When does it run: once at load, per session, per turn, per tool call?
3. What does it touch: files, network, subprocesses, credentials, the transcript?
4. Does it need UI? Extensions load in interactive, RPC, JSON, and print modes; only
   interactive mode has a terminal UI.
5. Personal (`~/.pi/agent/extensions/`), project (`.pi/extensions/`), or distributed as a
   Pi package?

## Step 2: Choose the integration point

| Capability | API |
|---|---|
| Observe or modify lifecycle behavior | `pi.on(event, handler)` |
| Model-callable operation | `pi.registerTool()` |
| `/command` | `pi.registerCommand()` |
| Keyboard shortcut / CLI flag | `pi.registerShortcut()` / `pi.registerFlag()` |
| Inject messages | `pi.sendMessage()` / `pi.sendUserMessage()` |
| Persist non-context session data | `pi.appendEntry()` |
| Change active tools, model, thinking level | `pi.setActiveTools()`, `pi.setModel()`, `pi.setThinkingLevel()` |
| Model provider | `pi.registerProvider()` |
| MCP server | `pi.registerMcpServer()` |
| Terminal rendering | `ctx.ui`, renderer registration |
| Talk to another extension | `pi.events` |

Read `references/api-reference.md` for the full API surface, the event catalog with each
event's result contract, and `ExtensionContext` contents. When an exact type matters, the
exported declarations in the installed package are authoritative:
`node_modules/@earendil-works/pi-coding-agent/dist/core/extensions/types.d.ts`.

## Step 3: Scaffold

Single file for a small extension; a directory with `index.ts` for a multi-file one. Copy
`assets/extension-template.ts` from this skill directory as a starting point.

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // register tools, commands, event handlers here — nothing else
}
```

Pi loads extensions with `jiti`: local TypeScript needs **no build step**. Pi supplies
`@earendil-works/pi-ai`, `@earendil-works/pi-agent-core`, `@earendil-works/pi-coding-agent`,
`@earendil-works/pi-tui`, and `typebox` — import from those freely. Other npm dependencies
go in a `package.json` next to the extension (see `assets/package-template.json`).

Locations: `~/.pi/agent/extensions/` (personal), `.pi/extensions/` (project, loads only
after project trust), or `pi --extension ./my-ext.ts` for development. Pi loads direct
`.ts`/`.js` files and subdirectories containing `index.ts`/`index.js`.

## Step 4: Respect the lifecycle

The rules that cause the most broken extensions — read `references/lifecycle.md` for the
full contract and reasoning:

- The factory may be sync or async (Pi awaits async before startup continues), but **do not
  start processes, sockets, watchers, or timers in it** — some invocations load extensions
  without starting a session. Start long-lived resources from `session_start` or lazily
  from the command/tool that needs them.
- Close session-scoped resources from an idempotent `session_shutdown` handler.
- Handlers run in load/registration order; `pi.on()` returns an unsubscribe function.
- Use each event's declared result type — some events notify only, others transform or
  cancel. Returning the wrong shape silently does nothing.
- Tool calls from one assistant message can run in parallel; never assume a sibling call
  or result exists.
- `turn_end` / `agent_before_settle` continuations must be guarded or they loop forever.
- Guard terminal-only behavior with `ctx.mode === "tui"`; use `ctx.hasUI` before dialogs.

## Step 5: Implement

Read `references/patterns.md` for worked, copy-adaptable patterns:

- custom tool (TypeBox params, `content` + `details`, errors, truncation, `outputSchema`)
- guard/confirm on `tool_call` and `user_bash`
- context and system-prompt modification (`before_agent_start`, `context`)
- command with UI, argument completions
- session state via tool-result `details` vs `appendEntry()` vs `sendMessage()`
- nested model calls via `ctx.modelRegistry.streamSimple()`
- provider / MCP registration
- tool exposure and dynamic activation

Also mine the checked-in examples — they are the implementation reference. Locally:
`<pi-install>/examples/extensions/` (70+ files: `hello.ts`, `todo.ts`, `protected-paths.ts`,
`permission-gate.ts`, `dynamic-tools.ts`, `structured-output.ts`, `subagent/`,
`custom-provider-anthropic/`, …). The docs map each example to its integration point
(`docs/extensions.md`, "Examples and reference"). Installed third-party packages under
`~/.pi/agent/npm/node_modules/` (e.g. `pi-web-access`, `pi-alibaba-models`) show
production-grade structure: multi-file layout, `pi` manifest in `package.json`,
peerDependencies on the pi packages.

## Step 6: Preflight and load-test

Run the bundled static checker (catches missing default export, side effects at module
scope, unguarded UI calls, common API misuse):

```bash
python3 <this-skill-dir>/scripts/check_extension.py <path-to-extension.ts-or-dir>
```

Then load it for real:

```bash
pi --extension ./my-ext.ts          # dev load, interactive
pi list                             # shows installed package extensions
```

Watch startup diagnostics for extension errors. In the session: exercise the command/tool,
check `/commands` if you registered slash commands, and confirm behavior in `--mode json`
or `-p` if the extension claims to work headless. After edits, `/reload` replaces the
extension runtime — code after reload must not reuse state from the old runtime.

## Step 7: Debug

- Extension errors are reported at load; a failing `tool_call` handler **blocks the tool**
  (fail-safe), and a failing `execute()` becomes an error tool result for the model.
- No UI in JSON/print modes: reproduce with `ctx.hasUI` checks, not by assuming a terminal.
- For provider/stream issues, see `examples/extensions/debug-provider.ts` and the
  `provider_stream_event` notes in `references/api-reference.md`.
- State that must follow session branching belongs in tool-result `details`, reconstructed
  from `ctx.sessionManager.getBranch()` on `session_start` — not from replaying every entry.

## Step 8: Package and distribute (optional)

For sharing via npm or git, use a Pi package: `package.json` with `"keywords":
["pi-package"]` and a `pi.extensions` array (or the conventional `extensions/` directory),
pi packages as `peerDependencies`, runtime deps in `dependencies`. Install with
`pi install npm:<pkg>` (`--local` for project scope). Full details in `docs/packages.md`
and `references/lifecycle.md` (packaging section).

## Security non-negotiables

Never write an extension that exfiltrates credentials, silently reads files outside the
task, phones home without disclosure, or hides destructive behavior. Destructive or
surprising capabilities must be explicit: confirm through `ctx.ui.confirm()`, gate behind
a command, and document them in the extension header and README. Project extensions run
with project trust — treat that trust as the user handing you their machine.
