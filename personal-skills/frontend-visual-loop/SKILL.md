---
name: frontend-visual-loop
description: Inspect real rendered UI while developing frontends by taking agent-browser screenshots that come back as actual images you can see, alongside console errors and page exceptions. Use when editing React/Vue/Svelte/HTML/CSS/JSX, after changing any component, layout, style, or route, when the user reports something "looks wrong", "is broken", "overlapping", "invisible", "misaligned", "check the page", "does this look right", "test the UI", "responsive check", "visual regression", or any request to verify what a browser renders. Also use before declaring frontend work complete. Requires the pi-agent-browser-native extension and the agent-browser CLI.
compatibility: Requires agent-browser >= 0.35.0 on PATH and the pi-agent-browser-native package. Chrome for Testing installed via `agent-browser install --with-deps`. A vision-capable model (input includes "image").
metadata:
  verified-on: "agent-browser 0.38.1 / pi 1.0.2 / WSL2 Ubuntu 24.04"
---

# Frontend visual loop

You cannot judge UI from source code. After every meaningful frontend change, render the
page in a real browser and look at it. Screenshots from the `agent_browser` tool arrive as
inline images in the tool result, so you see the actual pixels — a file path alone is not
evidence that you looked.

## The loop

1. **Start or reuse the dev server.** Launch it yourself in the background
   (`npm run dev &`), wait for its ready line, and confirm it answers:
   `curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/`. Never point the browser
   at a server you have not verified returns 200.
2. **Open the page** with `args: ["open", "<url>"]`, then confirm the browser is on it with
   `args: ["get", "url"]` — `about:blank` means the session is broken, not the page.
3. **Capture a checkpoint** (next section) — one call that returns screenshot + console + errors.
4. **Read the image before you judge.** Name the specific defect you see (overflowing text,
   invisible contrast, collapsed spacing, wrong element) and the file:line that causes it.
   If you cannot point at both, you have not diagnosed anything.
5. **Fix, then re-capture the same viewport.** Compare against the prior screenshot rather
   than trusting that your edit worked.
6. **Close when finished**: `args: ["close", "--all"]`. The browser daemon persists between
   calls and will outlive your turn otherwise.

## One call per checkpoint

Do not spend three tool calls on three commands. Batch them, and read the console and page
errors alongside the pixels — a page can look perfect while its script threw:

```json
{ "args": ["batch"], "stdin": "[[\"set viewport\",\"1280\",\"800\"],[\"open\",\"http://localhost:5173/\"],[\"wait\",\"500\"],[\"screenshot\",\"/abs/path/shot-desktop.png\"],[\"console\"],[\"errors\"]]" }
```

Always pass **absolute** screenshot paths and confirm the file exists where the result
claims. Relative paths have historically resolved against the long-lived browser daemon's
launch directory rather than your shell's cwd, which silently scatters artifacts across the
repo.

For a multi-viewport sweep in one shot, run the bundled script instead of hand-writing the
batch:

```bash
bash <this-skill-dir>/scripts/viewport-sweep.sh http://localhost:5173/ /abs/out-dir
```

It writes `mobile.png` (390x844), `tablet.png` (768x1024), `desktop.png` (1280x800) and
prints console/error output. Then `read` each PNG to actually see them.

## Viewports

| Target | Command | Why |
|---|---|---|
| Phone | `set viewport 390 844` | Catches overflow, unstacked flex rows, tap targets |
| Tablet | `set viewport 768 1024` | Breakpoint seams where grids go wrong |
| Desktop | `set viewport 1280 800` | Default; check before claiming done |
| Real device | `set device "iPhone 15 Pro"` | Adds DPR + UA, closer to hardware |

Desktop-only verification misses the most common frontend defects. Check at least phone and
desktop.

## Which command answers which question

| Question | Command |
|---|---|
| Does it look right? | `screenshot <abs.png>` — then look at the returned image |
| Anything whole-page? | `screenshot --full <abs.png>` |
| Did it break at runtime? | `console` and `errors` |
| Which element is which? | `screenshot --annotate` — overlays `[N]` labels matching `@eN` refs |
| Did my change alter pixels? | `diff screenshot --baseline <abs.png>` |
| What is clickable? | `snapshot -i` |
| Exact assertion (counts, computed style)? | `eval "<js>"` |
| Is it slow? | `vitals <url>` |
| Network failures? | `network requests` |

Use `eval` when a measurement beats eyeballing — `getComputedStyle(el).overflow`,
`document.body.scrollWidth > innerWidth` for horizontal overflow, element counts. It settles
questions a screenshot leaves ambiguous.

For React internals, launch with `open --enable react-devtools`, then `react tree`,
`react inspect <id>`, `react renders start|stop`, `react suspense`.

## Screenshot sparingly

Images stay in the transcript and are re-sent to the model on every subsequent request, so
ten checkpoints inflate the cost of all remaining turns. Capture at decision points — after
a component renders, after a layout fix, before declaring done — not after every keystroke.
Set `autoResizeImages` defaults keep oversized shots within provider limits; prefer JPEG for
large pages (`--screenshot-format jpeg --screenshot-quality 80`).

## Gotchas

- **Stale daemons screenshot blank pages.** If more than one `agent-browser` daemon is alive
  (common after a working directory is deleted, or when a Windows-side and a WSL-side install
  coexist), `open` and `screenshot` can land on different browsers. You get an all-white PNG
  that looks like a broken app, not a broken session. Symptoms: `[agent-browser] launched
  browser` repeating on every call, and `get url` returning `about:blank` right after a
  successful `open`. Recover with `agent-browser close --all`, then
  `pkill -f 'agent-[b]rowser-linux'`, and confirm with `agent-browser doctor`. Check
  `get url` before trusting any screenshot.
- **Install the CLI inside WSL, not on the Windows side.** A `/mnt/c/...` install runs the CLI
  over interop while Chrome for Testing runs natively, which makes relative paths resolve
  against the daemon's launch directory. `npm install -g agent-browser` from within WSL puts
  the whole toolchain on the Linux side.
- **`errors` prints a bare `✗`** in plain output when an exception has a multi-line stack.
  Add `--json` to get the real text.
- **`--annotate` cannot sit inside a batch step.** Put it in top-level `args` instead.
- **Wrapper version floor.** `pi-agent-browser-native` requires agent-browser >= 0.35.0;
  older CLIs fail until you `npm install -g agent-browser@latest`.
- **Anti-bot sites block you.** Google, httpbin, and many production sites serve CAPTCHAs to
  headless Chrome. Local dev servers and your own staging are unaffected; do not conclude
  your UI is broken when the page is a consent wall.
- **Blank page is usually your bug.** Check `console`/`errors` and the dev server log before
  blaming the browser.
- **No SSRF guard here.** `localhost`, private IPs, and `file://` are the point of this skill;
  for untrusted public browsing use a package with prompt-injection defenses instead.
