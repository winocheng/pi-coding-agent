# Extension API Reference

Condensed map of `ExtensionAPI`, the event catalog, and `ExtensionContext`. The exported
declarations are authoritative — for exact shapes open
`node_modules/@earendil-works/pi-coding-agent/dist/core/extensions/types.d.ts` in the
installed release, and `examples/extensions/` for working code.

## Table of contents

- [ExtensionAPI methods](#extensionapi-methods)
- [Event catalog](#event-catalog)
- [ExtensionContext](#extensioncontext)
- [ExtensionUIContext](#extensionuicontext)
- [Tool definition and result](#tool-definition-and-result)
- [Imports available without a package.json](#imports-available-without-a-packagejson)

## ExtensionAPI methods

Registration:

| Method | Purpose |
|---|---|
| `registerTool(tool)` | Model-callable tool (TypeBox `parameters`, `execute()`) |
| `registerCommand(name, { description, handler, getArgumentCompletions? })` | `/name` slash command |
| `registerShortcut(keyId, { description?, handler })` | Keyboard shortcut |
| `registerFlag(name, { description?, type: "boolean"\|"string", default? })` | CLI flag; read with `getFlag(name)` |
| `registerMessageRenderer(customType, renderer)` | Render `sendMessage()` content in the transcript |
| `registerEntryRenderer(customType, renderer)` | Render `appendEntry()` data in the transcript |
| `registerMarkdownTransformer(t)` | Transform rendered markdown |
| `registerProvider(name, config)` / `unregisterProvider(name)` | Model provider (see `docs/custom-provider.md`) |
| `registerMcpServer(name, config)` / `unregisterMcpServer(name)` | MCP server for this session |
| `registerVirtualModel(model)` / `unregisterVirtualModel(provider, id)` | Per-request model routing (`docs/virtual-models.md`) |

Events and messaging:

| Method | Purpose |
|---|---|
| `on(event, handler)` | Subscribe; returns an unsubscribe function |
| `events.on(name, cb)` / `events.emit(name, data)` | Cross-extension event bus |
| `sendMessage({ customType, content, display?, details? }, { triggerTurn?, deliverAs? })` | Custom message stored and sent to the model |
| `sendUserMessage(content, { deliverAs?, expandPromptTemplates? })` | Inject a user message |
| `appendEntry(customType, data?)` | Persist data outside model context |

Session and tool control:

| Method | Purpose |
|---|---|
| `getActiveTools()` / `setActiveTools(names)` | Tools declared to the model; unknown names ignored |
| `getAllTools()` | Every registered tool with `exposure`, `namespace`, `annotations` |
| `getExposure(name)` / `getNamespace(name)` | Tool metadata |
| `setModel(model)` / `getThinkingLevel()` / `setThinkingLevel(level)` | Model runtime |
| `setSessionName(name)` / `getSessionName()` / `setLabel(entryId, label)` | Session metadata |
| `getCommands()` | All slash commands with source info |
| `getSettings()` | Effective settings (read extension config from here) |
| `exec(command, args, options?)` | Run a subprocess |

## Event catalog

Handlers run in extension load and registration order. Use the declared result type; a
notify-only event ignores return values.

**Resources and trust**

| Event | Result contract |
|---|---|
| `project_trust` | Personal/CLI extensions only; runs before project extensions load |
| `resources_discover` | Contribute resource paths |

**Session lifecycle**

| Event | Result contract |
|---|---|
| `session_start` | notify — start long-lived resources here |
| `session_info_changed` | notify |
| `session_before_switch` / `session_before_fork` / `session_before_compact` | `{ cancel?: boolean }` (fork adds `skipConversationRestore`, compact adds `compaction`) |
| `session_compact` / `session_compact_failed` | notify |
| `session_before_tree` / `session_tree` | tree navigation |
| `session_shutdown` | notify — idempotent cleanup |
| `mcp_servers_change` | notify |

**Agent and turn lifecycle**

| Event | Result contract |
|---|---|
| `before_agent_start` | `{ message?, systemPrompt? }` — prefer mutating prompt sections/tools over replacing `systemPrompt`; the event also exposes `systemPromptOptions` |
| `agent_start` / `agent_end` | notify (`agent_end` can still be followed by retries, compaction, queued work) |
| `agent_before_settle` | `BoundaryResult` — final actionable boundary; can append entries and request **one** continuation |
| `agent_settled` | notify only — Pi will not continue automatically |
| `turn_start` / `turn_end` | `turn_end` returns `BoundaryResult`; can chain `custom`, `custom_message`, `context_edit`, `compaction` entries and `continue: true` |
| `ui_prompt_start` / `ui_prompt_end` | notify |

**Messages and context**

| Event | Result contract |
|---|---|
| `message_start` / `message_update` | notify |
| `message_end` | `{ message? }` — replace the finalized message, must keep its role |
| `context` | `{ messages? }` — transform conversation messages *without* system messages; Pi restores them after |
| `context_with_system` | same, but you own the complete transcript; keep a system message at index 0 |
| `cache_warming_decision` | `{ action: "warm" \| "stop" }` — last handler returning an action wins |

**Providers**

| Event | Result contract |
|---|---|
| `before_provider_request` / `before_provider_headers` / `after_provider_response` | request/response interception |
| `provider_stream_event` | notify only, **not persisted**; `event.data` is the earliest structured value Pi has, treat as read-only; handlers are awaited in stream order so slow handlers delay consumption |

**Tools and input**

| Event | Result contract |
|---|---|
| `tool_call` | `{ block?, reason?, terminate? }` — mutate `event.input` in place to change arguments; handler failure **blocks the tool** (fail-safe) |
| `tool_result` | `{ content?, details?, structuredContent?, isError?, usage? }` — handlers compose, each sees prior changes; if you redact `content`, also replace `structuredContent` |
| `tool_execution_start` / `_update` / `_end` | notify; carry `parentToolCallId` for nested calls |
| `user_bash` | `{ operations }` or `{ result }` stops propagation; `undefined` passes to the next handler, then local execution. Handler failure blocks the command |
| `input` | raw user input, before commands/templates |
| `model_select` / `thinking_level_select` | notify |

## ExtensionContext

Available to event handlers, tool `execute()`, and command handlers:

- `ui` — dialogs, notifications, status, widgets, editor, custom components
- `mode` — `"tui" | "rpc" | "json" | "print"`; guard terminal-only UI with `mode === "tui"`
- `hasUI` — true in TUI and RPC modes (dialog-capable)
- `cwd`, `signal` (undefined when not streaming), `model`, `scopedModels`, `thinkingLevel`
- `sessionManager` (read-only; `getBranch()` for branch-sensitive state)
- `modelRegistry` — `streamSimple()` for provider-neutral nested model calls
- `isIdle()`, `isProjectTrusted()`, `hasPendingMessages()`, `abort()`, `shutdown()`
- `getContextUsage()`, `compact(options?)`, `getSystemPrompt()`

`ExtensionToolContext` (tool `execute()`) adds `tools` and
`executeTool(name, args, { signal?, onUpdate? })`. Nested calls go through validation and
the `tool_call`/`tool_result` handlers, get ids `<parent>/<n>`, and never appear in the
transcript — the calling tool must report them itself. Their `usage` rolls up into the
caller's result, so a tool reports only its own usage. `executeTool()` never rejects for
tool failures; failures come back as `isError: true`.

`ExtensionCommandContext` (command handlers) adds `getSystemPromptOptions()`,
`waitForIdle()`, `newSession()`, `fork()`, `withSession()`, `reload()`, and tree
navigation. These are command-only: calling them from lifecycle handlers can deadlock the
runtime. Session replacement invalidates the old context — capture plain data first, then
use the fresh context from `withSession`.

## ExtensionUIContext

`notify(message, level)`, `confirm(title, message)`, `select(title, items)`, `prompt(...)`,
`setStatus(key, text)`, `setWidget(key, content, options?)`, `setFooter()` / `setHeader()` /
`setTitle()`, `setWorkingMessage()` / `setWorkingIndicator()` / `setHiddenThinkingLabel()`,
`setEditorText()` / `getEditorText()`, `setEditorComponent()`, `custom()` (own rendering and
input), `onTerminalInput()`, theme access (`getAllThemes()`, `getTheme()`, `setTheme()`),
overlay handling. See `docs/tui.md` for components, focus, overlays, and performance.

RPC mode can forward supported dialogs and notifications (`docs/rpc-extension-ui.md`) but
not custom terminal components; JSON and print modes have no UI at all. Keep tool and event
behavior independent of rendering so headless modes keep working.

## Tool definition and result

```typescript
{
  name: string;                  // used in LLM tool calls
  label: string;                 // UI label
  description: string;           // model-facing
  promptSnippet?: string;        // one line for "Available tools" in the system prompt
  promptGuidelines?: string[];   // bullets appended to Guidelines when active
  parameters: TSchema;           // TypeBox
  outputSchema?: TSchema;        // when the result is data; return matching structuredContent
  exposure?: "direct" | "model-only" | "codemode" | "deferred" | "hidden";
  namespace?: { name, description, instructions? };
  annotations?: { readOnlyHint?, destructiveHint?, idempotentHint?, openWorldHint? };
  execute(toolCallId, params, signal, onUpdate, ctx): Promise<AgentToolResult>;
}
```

Result: `{ content: (TextContent | ImageContent)[], details: unknown, structuredContent?,
isError?, usage?, terminate? }`.

- `content` is model-facing; `details` is for rendering and state reconstruction (use
  `undefined` when there is nothing structured).
- **Throw** from `execute()` to produce a failed result — returning an object is not an
  error. To report failure that still carries data, return it with `isError: true`.
- `terminate: true` only ends the agent when every completed tool in the batch agrees.
- Truncate large model-facing output and tell the model where to read the rest.
- Include nested model-call `usage` so session totals stay accurate.
- Tools sharing mutable in-memory state need sequential execution; file-mutating tools
  should wrap the whole read-modify-write in `withFileMutationQueue()`.

Exposure: `direct` (default: declared and callable while active), `model-only` (declared,
never callable — good for orchestrators), `codemode` (callable always, listed by the
`codemode` tool), `deferred` (callable, not listed; `tool_search` can activate it),
`hidden` (registered but unreachable — the way to withdraw a tool, since tools cannot be
unregistered). Registering `direct`/`model-only` activates the tool; others start inactive.

## Imports available without a package.json

Pi supplies these to extensions and skills, so they resolve with no local install:

```typescript
import type { ExtensionAPI, ExtensionContext, Theme } from "@earendil-works/pi-coding-agent";
import { defineTool } from "@earendil-works/pi-coding-agent";
import { Type, StringEnum } from "@earendil-works/pi-ai";   // or: import { Type } from "typebox";
import { Text, Box, matchesKey, truncateToWidth } from "@earendil-works/pi-tui";
```

Anything else needs a `package.json` with `dependencies` next to the extension (jiti
resolves from the extension's own `node_modules`), or a Pi package that declares them.
