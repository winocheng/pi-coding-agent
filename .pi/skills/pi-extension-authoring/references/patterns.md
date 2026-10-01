# Extension Patterns

Worked patterns for the common integration points. Each is adapted from the checked-in
examples in `<pi-install>/examples/extensions/` — when a pattern here is not enough, open
the matching example file; the examples are the implementation reference.

## Table of contents

- [Custom tool](#custom-tool)
- [Guarding tool calls and bash](#guarding-tool-calls-and-bash)
- [Slash command with UI](#slash-command-with-ui)
- [Modifying the system prompt and context](#modifying-the-system-prompt-and-context)
- [Session state](#session-state)
- [Nested model calls](#nested-model-calls)
- [Injecting messages and continuations](#injecting-messages-and-continuations)
- [Providers and MCP servers](#providers-and-mcp-servers)
- [Dynamic tools](#dynamic-tools)
- [Status and widgets](#status-and-widgets)

## Custom tool

Minimal shape (`hello.ts`). `defineTool` gives you type inference on params:

```typescript
import { defineTool, type ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

const searchTool = defineTool({
  name: "issue_search",
  label: "Issue Search",
  description: "Search the issue tracker. Returns titles, ids, and states.",
  // Optional: one line for the system prompt's "Available tools" section,
  // and guideline bullets appended while the tool is active.
  promptSnippet: "Search issues by keyword",
  promptGuidelines: ["Prefer issue_search over asking the user for issue ids."],
  parameters: Type.Object({
    query: Type.String({ description: "Search keywords" }),
    limit: Type.Optional(Type.Number({ description: "Max results (default 10)" })),
  }),

  async execute(_toolCallId, params, signal, _onUpdate, ctx) {
    // Throw to produce a failed tool result — returning is never an error.
    if (!params.query.trim()) throw new Error("query must not be empty");

    const results = await searchIssues(params.query, params.limit ?? 10, signal);

    // Truncate model-facing output; tell the model where the rest lives.
    const text = results.map((r) => `#${r.id} [${r.state}] ${r.title}`).join("\n");
    return {
      content: [{ type: "text", text: truncate(text, 40_000) }],
      details: { results },            // for rendering / state reconstruction
      // When the result is data, declare outputSchema + structuredContent so
      // codemode scripts can consume it programmatically.
    };
  },

  // Optional custom rendering in the transcript (see todo.ts, structured-output.ts).
  renderResult(result, _options, theme) { /* return a pi-tui Component */ },
});

export default function (pi: ExtensionAPI) {
  pi.registerTool(searchTool);
}
```

Rules that matter: include `usage` from any nested model calls; wrap file
read-modify-write in `withFileMutationQueue()`; `terminate: true` only when the agent
should stop right after this tool (all tools in the batch must agree — see
`structured-output.ts`).

## Guarding tool calls and bash

Block or confirm dangerous operations (`protected-paths.ts`, `permission-gate.ts`,
`confirm-destructive.ts`). A `tool_call` handler mutates `event.input` in place to change
arguments, or returns `{ block, reason }`:

```typescript
export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return undefined;

    const cmd = String(event.input.command ?? "");
    if (!/rm\s+-rf|sudo|mkfs/.test(cmd)) return undefined;

    // hasUI is true in tui + rpc modes; headless modes must fall back to a policy.
    if (!ctx.hasUI) return { block: true, reason: "Destructive command needs approval; no UI available." };

    const ok = await ctx.ui.confirm("Dangerous command", cmd);
    if (!ok) return { block: true, reason: "User rejected the command." };
    return undefined; // proceed
  });
}
```

Remember: a handler that *throws* blocks the tool (fail-safe). `tool_result` handlers
compose — each sees prior handlers' changes; if you redact `content`, replace
`structuredContent` too. For `user_bash` (`!` commands), returning `undefined` passes to
the next handler and then local execution; returning `operations` or `result` takes over;
a handler failure blocks the command.

Approval based on MCP-style annotations (from the docs — confirms what Codex asks about):

```typescript
pi.on("tool_call", async (event, ctx) => {
  const hints = pi.getAllTools().find((t) => t.name === event.toolName)?.annotations;
  const needsApproval =
    hints?.destructiveHint === true ||
    (!hints?.readOnlyHint && ((hints?.destructiveHint ?? true) || (hints?.openWorldHint ?? true)));
  if (needsApproval && !(await ctx.ui.confirm("Allow tool call?", event.toolName))) {
    return { block: true, reason: `${event.toolName} was not approved` };
  }
});
```

## Slash command with UI

`registerCommand` handler receives `(args, ctx: ExtensionCommandContext)` — the only place
`waitForIdle()`, `newSession()`, `fork()`, `withSession()`, `reload()` are safe
(`commands.ts`, `tools.ts`, `handoff.ts`):

```typescript
export default function (pi: ExtensionAPI) {
  pi.registerCommand("deploy", {
    description: "Deploy the current branch",
    getArgumentCompletions: (prefix) =>
      ["staging", "prod"].filter((e) => e.startsWith(prefix)).map((value) => ({ value, label: value })),
    handler: async (args, ctx) => {
      const env = args.trim() || "staging";
      if (ctx.hasUI && !(await ctx.ui.confirm("Deploy", `Deploy to ${env}?`))) return;
      ctx.ui.setStatus("deploy", `deploying to ${env}…`);
      try {
        const result = await pi.exec("./scripts/deploy.sh", [env]);
        ctx.ui.notify(result.exitCode === 0 ? `Deployed to ${env}` : result.stderr, result.exitCode === 0 ? "info" : "error");
      } finally {
        ctx.ui.setStatus("deploy", undefined); // clear
      }
    },
  });
}
```

## Modifying the system prompt and context

`before_agent_start`: prefer changing prompt **sections**, selected tools, or guidelines so
Pi can append a transcript delta. Returning `systemPrompt` replaces the entire prompt for
that run (the transcript keeps recording structured sections; providers get the forced
text). `context` transforms conversation messages *without* system messages; use
`context_with_system` only when a request-local transformation must own the complete
transcript, keeping a system message at index 0 (`system-prompt-header.ts`,
`claude-rules.ts`, `prompt-customizer.ts`).

## Session state

Pick storage by how state participates in the conversation:

| State | Storage |
|---|---|
| Tool state that follows the active branch | Tool-result `details` (`todo.ts` — branching gets the right state for free) |
| Durable data excluded from model context | `pi.appendEntry(customType, data)` + `registerEntryRenderer` |
| Custom content stored and sent to the model | `pi.sendMessage({ customType, content, details })` + `registerMessageRenderer` |
| Data outside one session | External storage (files, DB) keyed by something stable |

Reconstruct branch-sensitive state from `ctx.sessionManager.getBranch()` during
`session_start` — never by replaying every file entry, because abandoned branches are
alternative histories.

## Nested model calls

Use the model registry for provider-neutral calls (`custom-compaction.ts`):

```typescript
const model = ctx.modelRegistry.find("google", "gemini-2.5-flash");
if (!model) return; // always handle "model not available"
const response = await ctx.modelRegistry.complete(
  model,
  { messages: [{ role: "user", content: [{ type: "text", text: prompt }], timestamp: Date.now() }] },
  { maxTokens: 8192, signal: ctx.signal, sessionId: uuidv7() },
);
const text = response.content.filter((c) => c.type === "text").map((c) => c.text).join("\n");
```

Pass `signal` so user aborts propagate, and fold `response.usage` into your tool result's
`usage`. A tool can also run other tools with `ctx.executeTool(name, args, { signal,
onUpdate })` — nested calls go through validation and the `tool_call`/`tool_result`
handlers, never reject for tool failures (`isError: true` instead), and don't appear in the
transcript: report them yourself via `onUpdate`/`details`.

## Injecting messages and continuations

- `pi.sendUserMessage(content, { deliverAs: "steer" | "followUp" })` — inject user input
  (`send-user-message.ts`).
- `pi.sendMessage({ customType, content, display?, details? }, { triggerTurn?: boolean })` —
  custom stored message (`entry-renderer.ts`, `message-renderer.ts`).
- `turn_end` / `agent_before_settle` handlers may append `custom`, `custom_message`,
  `context_edit`, or `compaction` entries and return `continue: true` for **one** next
  model request. Guard the condition or it loops (`trigger-compact.ts`, `handoff.ts`).

## Providers and MCP servers

`registerProvider` works three ways (full guide: `docs/custom-provider.md`; examples:
`custom-provider-anthropic/`, `custom-provider-gitlab-duo/`; production: the installed
`pi-alibaba-models` package):

```typescript
// 1. New provider with models
pi.registerProvider("my-proxy", {
  baseUrl: "https://proxy.example.com",
  apiKey: "$PROXY_API_KEY",           // env-var reference
  api: "anthropic-messages",          // or "openai-responses", "openai-completions", ...
  models: [{ id: "...", name: "...", reasoning: false, input: ["text"],
             cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
             contextWindow: 200000, maxTokens: 16384 }],
});
// 2. Override baseUrl of an existing provider
pi.registerProvider("anthropic", { baseUrl: "https://proxy.example.com" });
// 3. Custom API: supply streamSimple (must call options.onPayload / onResponse)
```

Calls during initial load are queued and applied once the runner binds; later calls take
effect immediately (no `/reload` needed). `oauth: { name, login, refreshToken, getApiKey }`
adds `/login` support.

MCP (`docs/mcp.md`): `pi.registerMcpServer("jira", { url, headers?, oauth? })` or stdio
`{ command, args, env, cwd }`, plus `exposure`, `toolExposure`, `description`, `enabled`,
`timeout`. Registrations are **not saved** — register on every load. A same-named server in
`mcp.json` wins. Servers registered at load connect at session start; later registrations
connect right away; `unregisterMcpServer()` closes and removes its tools.

## Dynamic tools

Register all tools at load, keep optional ones inactive (`exposure: "codemode"` or
`"deferred"`), then select the active set from a loader tool or command with
`pi.setActiveTools([...names])` — unknown names are ignored. Pi records the initial tool
set in the first system message and appends deltas before the next model request;
providers that cannot represent the transition get a full checkpoint, which can invalidate
the cached prompt prefix — so avoid churn mid-conversation (`dynamic-tools.ts`,
`tools.ts`). To withdraw a tool, re-register it with `exposure: "hidden"`; tools cannot be
unregistered.

## Status and widgets

```typescript
ctx.ui.setStatus("my-key", "building…");        // footer status; undefined clears
ctx.ui.setWidget("my-widget", ["line 1"], { placement: "aboveEditor" }); // or belowEditor
ctx.ui.setTitle("my-project");
ctx.ui.setWorkingIndicator({ /* frames, interval */ });
```

For anything with its own rendering and input, use `ctx.ui.custom()` with a pi-tui
component (`status-line.ts`, `widget-placement.ts`, `border-status-editor.ts`; component
and focus guidance in `docs/tui.md`). Custom components only render in `tui` mode — keep
the underlying behavior mode-independent.
