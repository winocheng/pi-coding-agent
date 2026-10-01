/**
 * my-extension — one-line summary of what it adds to Pi.
 *
 * What it registers:
 *   - tool `my_tool`    — what the model can do with it
 *   - command `/my-cmd` — what the user can run
 *   - handler `tool_call` — what it guards or transforms
 *
 * Modes: works in tui/rpc; headless modes fall back to <policy>.
 */

import { defineTool, type ExtensionAPI, type ExtensionContext } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

// Module scope: types, constants, pure helpers only.
// No processes, sockets, watchers, or timers here — some invocations load
// extensions without starting a session. Start those from session_start.

interface MyState {
	// session-scoped state; reconstruct from ctx.sessionManager.getBranch() if branch-sensitive
}

let state: MyState | undefined;
let longLivedResource: { close(): void } | undefined;

const myTool = defineTool({
	name: "my_tool",
	label: "My Tool",
	description: "Model-facing description: what it does and when to use it.",
	parameters: Type.Object({
		target: Type.String({ description: "What to operate on" }),
	}),

	async execute(_toolCallId, params, signal, _onUpdate, ctx) {
		// Throw to fail; returning an object is never an error.
		if (signal?.aborted) throw new Error("aborted");
		const output = await doWork(params.target, ctx);
		return {
			content: [{ type: "text", text: output }],
			details: { target: params.target },
		};
	},
});

export default function (pi: ExtensionAPI) {
	pi.registerTool(myTool);

	pi.registerCommand("my-cmd", {
		description: "User-facing one-liner",
		handler: async (args, ctx) => {
			if (ctx.hasUI && !(await ctx.ui.confirm("My Command", `Run on "${args}"?`))) return;
			ctx.ui.notify(`Running on ${args || "(nothing)"}`, "info");
		},
	});

	pi.on("session_start", async (_event, ctx) => {
		state = {};
		// Start long-lived resources here, not in the factory.
		// longLivedResource = startSomething(ctx);
	});

	pi.on("tool_call", async (event, ctx) => {
		// Return undefined to pass through; { block, reason } to stop.
		// A throwing handler blocks the tool as a fail-safe.
		if (event.toolName !== "bash") return undefined;
		return undefined;
	});

	pi.on("session_shutdown", async () => {
		// Idempotent: cancellation, reload, session replacement, and exit can all land here.
		longLivedResource?.close();
		longLivedResource = undefined;
		state = undefined;
	});
}

async function doWork(target: string, _ctx: ExtensionContext): Promise<string> {
	return `did work on ${target}`;
}
