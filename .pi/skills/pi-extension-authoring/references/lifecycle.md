# Lifecycle, Loading, and Packaging

The runtime contract behind the rules in SKILL.md, plus where extensions load from and how
to ship one.

## Table of contents

- [Load order and discovery](#load-order-and-discovery)
- [The factory contract](#the-factory-contract)
- [Run lifecycle](#run-lifecycle)
- [Concurrency](#concurrency)
- [Reload semantics](#reload-semantics)
- [Errors and cleanup](#errors-and-cleanup)
- [Modes](#modes)
- [Packaging](#packaging)

## Load order and discovery

Pi loads direct `.ts`/`.js` files and subdirectories containing `index.ts`/`index.js` from:

- `~/.pi/agent/extensions/` — personal
- `.pi/extensions/` — project (only after project trust is granted)
- `pi --extension <path>` (`-e`) — explicit, one invocation or development
- Pi packages declared in settings (`pi install npm:<pkg>`, `--local` for project scope)
- Additional paths via the `extensions` setting (supports `!glob` exclusions, `+path`
  inclusion, `-path` exclusion)

Handlers run in extension load and registration order. `pi.on()` returns a function that
unsubscribes that registration; unsubscribing does not affect a dispatch already in
progress. Only personal and explicit CLI extensions can participate in `project_trust`,
which runs before project extensions load.

## The factory contract

The default export receives `ExtensionAPI` and registers capabilities. It may be sync or
async; Pi awaits an async factory before startup continues, which is the place to fetch
configuration or register providers needed during startup.

**Do not start processes, sockets, file watchers, or timers in the factory.** Some
invocations load extensions without ever starting a session (validation passes, `pi list`,
headless one-shots), so anything started at load time can leak or run with no owner. Start
long-lived resources from `session_start`, or lazily from the command or tool that first
needs them, and track what you started so `session_shutdown` can stop it.

Reading settings (`pi.getSettings()`), registering tools/commands/handlers, and pure
computation are safe at load time.

## Run lifecycle

A run proceeds: user input → `input` → `before_agent_start` → model/message/tool events →
`agent_end`. Automatic retries, recovery, compaction, or queued work can continue after
`agent_end`.

- `agent_before_settle` is the **final actionable boundary**: it can append entries and
  request one continuation.
- `agent_settled` is final and notification-only — use it when an integration needs to know
  Pi will not continue on its own (e.g. fire a notification, flush metrics).

`turn_end` and `agent_before_settle` handlers can chain proposed `custom`,
`custom_message`, `context_edit`, or `compaction` entries and return `continue: true` for
one next model request. **Guard the continuation condition.** An unconditional
`continue: true` loops forever and burns tokens; check the state that should end the loop
before returning it.

## Concurrency

Tool calls from a single assistant message can execute in parallel. Do not assume a sibling
call or result exists when your handler runs, and do not share mutable state between
concurrent `execute()` invocations without synchronization. Tools that need shared
in-memory state should run sequentially; file-mutating tools should wrap the complete
read-modify-write in `withFileMutationQueue()`.

Use `ctx.signal` for nested work owned by an active turn so aborts propagate. Commands and
idle session events often have no operation signal — handle `undefined`.

## Reload semantics

`/reload` replaces the extension runtime. Code after `await ctx.reload()` must not reuse
state from the old runtime: re-read files, re-resolve config, and re-register. Design
module-level caches so a fresh import starts clean.

Session replacement (`ctx.withSession`) invalidates the old context. Capture only plain
data before switching, then use the fresh context supplied to `withSession` for
session-bound work.

## Errors and cleanup

Pi reports handler errors and continues where possible, with two fail-safe exceptions:

- A failing `tool_call` handler **blocks the tool call** rather than allowing it.
- A failing `execute()` becomes an error tool result for the model (equivalent to throwing).

Release resources in `session_shutdown` even when normal operation already attempted
cleanup, and keep cleanup **idempotent**: cancellation, reload, session replacement, and
process exit can all converge on the same path. `ctx.shutdown()` requests an orderly
process shutdown.

## Modes

Extensions load in all four modes:

| Mode | UI | Notes |
|---|---|---|
| `tui` | Full terminal UI | Custom components, overlays, widgets |
| `rpc` | Forwarded dialogs/notifications | Via the RPC Extension UI protocol; no custom components |
| `json` | None | Structured output |
| `print` | None | `-p` one-shot |

Guard terminal-only behavior with `ctx.mode === "tui"`, and any dialog with `ctx.hasUI`
(true in tui and rpc). Keep tool and event behavior independent from rendering so
headless modes stay functional — an extension that only works interactively silently
breaks scripting users.

## Packaging

For anything shared through npm or git, use a Pi package. Minimal `package.json`:

```json
{
  "name": "my-pi-extension",
  "version": "0.1.0",
  "type": "module",
  "keywords": ["pi-package"],
  "pi": { "extensions": ["./extensions/my-ext.ts"] },
  "peerDependencies": { "@earendil-works/pi-coding-agent": "*" },
  "dependencies": { "some-lib": "^1.0.0" }
}
```

- `keywords: ["pi-package"]` makes it discoverable as a package.
- The `pi` manifest lists resources explicitly; without it Pi discovers TypeScript/JS
  extensions from a conventional `extensions/` directory. Use the manifest when files live
  elsewhere or need filtering. Paths are relative to the package root; arrays accept globs.
- Pi packages as `peerDependencies` (Pi supplies them at runtime); real runtime deps in
  `dependencies` — Pi installs them when installing an npm or git source.
- A package can also expose `skills`, `prompts`, and `themes` arrays.
- No build step is required (jiti loads TypeScript), but packages that prebuild (esbuild/tsc
  into `dist/`) point `pi.extensions` at the built output — see `pi-web-access` under
  `~/.pi/agent/npm/node_modules/` for a production example, and `pi-alibaba-models` for a
  provider extension shipped as raw `.ts` with `files` limited to `extensions/**/*.ts`.

Install and manage:

```bash
pi install npm:my-pi-extension        # personal (writes ~/.pi/agent/settings.json)
pi install npm:my-pi-extension -l     # project (writes .pi/settings.json, needs trust)
pi list                               # installed extensions from settings
pi update <source>                    # update one; pi update self/pi for others
pi -e npm:my-pi-extension             # try once without adding to settings
pi remove <source>
```

Project packages install and load only after project trust is resolved, and can execute
extension code — review third-party sources before installing, and review project package
declarations before granting trust.
