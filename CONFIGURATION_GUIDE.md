# Pi Coding Agent — Configuration Guide

This document walks through the full setup process for configuring the Pi coding agent with Alibaba Cloud models.

> **Extension source changed (2026-10-04).** This guide previously installed the Alibaba provider with
> `pi install npm:pi-alibaba-models`. That npm package is the **original upstream** release and has no
> fork equivalent published — the maintained fork we now document,
> [`RarogCmex/pi-alibaba-models`](https://github.com/RarogCmex/pi-alibaba-models), is installed from git.
> If Pi is already configured with the npm package, do [step 4](#4-migrate-off-the-npm-package) first.

---

## Table of Contents

1. [Install Pi](#1-install-pi)
2. [Node.js And npm Under WSL](#2-nodejs-and-npm-under-wsl)
3. [Install the Alibaba Models Extension](#3-install-the-alibaba-models-extension)
4. [Migrate Off The npm Package](#4-migrate-off-the-npm-package)
5. [Start Pi](#5-start-pi)
6. [Configure Alibaba Cloud Domain](#6-configure-alibaba-cloud-domain)  
   *Optional — skip if using the default International endpoint*
7. [Login with an Alibaba API Key](#7-login-with-an-alibaba-api-key)
8. [Configure Scoped Models](#8-configure-scoped-models)
9. [Optional: DashScope Sidecar And Image Tools](#9-optional-dashscope-sidecar-and-image-tools)
10. [Configure Web Search with Exa](#10-configure-web-search-with-exa)
11. [Install the Ask-User-Question Extension](#11-install-the-ask-user-question-extension)
12. [Set Up OpenSpec for Spec-Driven Planning](#12-set-up-openspec-for-spec-driven-planning)
13. [Frontend Visual Loop: Browser Screenshots The Model Can See](#13-frontend-visual-loop-browser-screenshots-the-model-can-see)
14. [Update / Uninstall The Alibaba Extension](#14-update--uninstall-the-alibaba-extension)
15. [Git Push Auth Under WSL](#git-push-auth-under-wsl)
16. [Troubleshooting The Swap](#troubleshooting-the-swap)
17. [Project-Local And Personal Skills](#project-local-and-personal-skills)
18. [Summary](#summary)

---

## 1. Install Pi

Download and run the official installer script:

```bash
curl -fsSL https://pi.dev/install.sh | sh
```

This installs the Pi coding agent CLI to your system.

> **Version floor.** The Alibaba fork requires Pi **1.0.0 or newer** and refuses to start with a clear
> diagnostic on older hosts (`pi --version` to check). The last fork release that runs on pre-1.0.0
> hosts is 1.5.3.

---

## 2. Node.js And npm Under WSL

Pi bundles its own Node.js and puts it first on `PATH`, so inside a Pi session `node`, `npm`, and `npx`
all resolve to Pi's copy. A plain terminal does **not** inherit that: on a fresh shell `node` falls back
to the old apt build (v18, which ships no `npm` at all), and `npm` may resolve to a Windows-side copy
over interop. That mismatch is the root of most "why did this install land somewhere weird" confusion,
so make Pi's Node the default everywhere.

### What is actually installed here

| Node | Version | Where | Notes |
|---|---|---|---|
| Pi-managed (recommended) | v22.23.3 | `~/.local/share/pi-node/current/bin` | Installed by the Pi installer; satisfies Pi's `>=22.19.0` floor; `npm prefix` points here |
| apt `nodejs` | v18.19.1 | `/usr/bin/node` | Outdated and ships no npm — shadow or remove it |
| Windows (nvm4w / Program Files) | v22.13.1 | `/mnt/c/...` | Reachable only via interop; do not use it for WSL work |

### Make Pi's Node the default

Pi's launcher prepends `~/.local/share/pi-node/current/bin` to `PATH` only for the `pi` process. Add the
same line to your shell profile so every terminal agrees:

```bash
cat << 'EOF' >> ~/.bashrc

# Use Pi's bundled Node.js as the default node/npm (matches what pi itself runs on)
export PATH="$HOME/.local/share/pi-node/current/bin:$PATH"
EOF
source ~/.bashrc
```

Verify in a **new** terminal:

```bash
node --version          # v22.23.3
npm --version           # 10.x
which -a node           # pi-node first, then /usr/bin/node
npm config get prefix   # ~/.local/share/pi-node/...
```

Now `npm install -g <tool>` (agent-browser, openspec, …) lands in Pi's Node tree and on `PATH`, and
`pi install npm:…` resolves packages against the same Node — so what you install is what Pi runs.

> **Interactive shells only.** `.bashrc` is read by interactive terminals; non-interactive shells
> (scripts, cron, `bash -c`) skip it via the standard `case $-` guard near the top of the file. Pi's
> own installs are unaffected — the launcher prepends Pi's Node inside the `pi` process — but if a
> script invokes `npm` directly, add the same `export` to `~/.profile` as well.

> **Why not nvm?** Microsoft's WSL guidance recommends a version manager, and nvm is the right tool if
> you do general Node development across many versions. But Pi already ships and pins its own Node, and
> Pi always runs on that copy regardless of nvm. For a Pi-centric setup, letting Pi's Node be the
> default is simpler and avoids two managers fighting over `PATH`. Install nvm only for non-Pi projects
> that need a different version — and keep Pi's Node ahead of it on `PATH`.

> **The version floor matters.** Pi requires Node `>=22.19.0`, and its package manager resolves packages
> against that Node. A package that declares a newer engine (for example one needing Node 24) is
> deliberately installed at the newest version that runs under Pi's Node — that is correct behaviour,
> not a bug. Upgrading Node on your own will not make Pi use it; Pi runs on its bundled copy.

### Clean up the strays (optional)

- **apt Node** is outdated and ships no npm. Once Pi's Node is first on `PATH` it is harmless but
  confusing; remove it with `sudo apt remove nodejs` if nothing else depends on it
  (`apt-cache rdepends --installed nodejs`).
- **Windows Node** (`/mnt/c/nvm4w`, `/mnt/c/Program Files/nodejs`) leaks into WSL `PATH` because
  `appendWindowsPath` defaults to true. Leave it for Windows-side tools; Pi's Node wins on `PATH` order
  so it will not interfere. Setting `appendWindowsPath=false` in `/etc/wsl.conf` removes the clutter but
  also hides other Windows executables — only do that deliberately.

---

## 3. Install the Alibaba Models Extension

Install the Alibaba provider from the maintained fork:

```bash
pi install git:github.com/RarogCmex/pi-alibaba-models
```

Or from a local checkout (useful for pinning a commit or hacking on it):

```bash
git clone https://github.com/RarogCmex/pi-alibaba-models
cd pi-alibaba-models && pi install .
```

> **The fork is never published to npm.** `pi install npm:pi-alibaba-models` and
> `pi install pi-alibaba-models` both resolve the **original upstream** package, not this fork.

Restart Pi in a **new session** after installing (more reliable than `/reload` for provider
registration). On boot the extension registers two providers — `alibaba-plan` and `alibaba-cloud` —
the `/alibaba` command, the DashScope sidecar tool (`alibaba_tools`), and image models/tools.

Verify:

```bash
pi list                                     # the git source should appear, and npm:pi-alibaba-models should NOT
pi --offline --list-models alibaba-cloud    # real model ids from the cached catalogue
```

### Why the fork instead of the npm package

| | npm `pi-alibaba-models` (1.1.1) | fork (2.0.0) |
|---|---|---|
| Cloud wire format | `anthropic-messages` default, `openai-completions` selectable — **no Responses** | **OpenAI Responses by default**, auto-fallback to Chat Completions for models without Responses support, Anthropic still selectable |
| Output budget | card `maxTokens` 8192 → only ~1024 tokens left for the answer at high thinking, so long replies are truncated mid-sentence with `stopReason: length` | uses the catalogue's real `max_output_tokens` (clamped at 131072) |
| Endpoints | International / China | International / China / US-Virginia / Hong Kong / **workspace domains** / Custom |
| API key swap | keeps the old key's endpoint — every request then fails `403` | endpoint **re-derived from the new key**: verified against shared regional defaults first, then upgraded to that key's own workspace domain |
| Catalogue | static list shipped in the package | **live** Alibaba catalogue (`GET /api/v1/models`) plus an offline snapshot, so new models appear without an extension update |
| Two installs at once | a stale npm copy silently overrides the newer one (no diagnostic) | **duplicate-install guard** — Pi refuses to start and names the copy to remove |
| Extra capabilities | chat only | native thinking levels, vision, `alibaba_tools` sidecar (web search / extract / code interpreter / image search), DashScope image generation, per-model context-window override |

---

## 4. Migrate Off The npm Package

Do this once if `pi list` shows `npm:pi-alibaba-models` (i.e. following step 3 above installed the git
fork while the npm copy is still configured). Two copies register the same `alibaba-cloud` provider, and
the fork's guard makes Pi fail at startup with:

```
pi-alibaba-models is installed 2 times; 1 of those would shadow this copy in the same pi process.
```

Remove the stale npm copy, then restart:

```bash
pi remove npm:pi-alibaba-models
rm -rf ~/.pi/agent/npm/node_modules/pi-alibaba-models   # only if it lingers in `pi list`
```

`pi remove` edits `~/.pi/agent/settings.json` (`packages`) but leaves extension-private state behind,
which is what you want here — the existing key and domain config carry over to the fork. To start from a
clean slate instead, wipe the fork's state too (you will need to `/login` again):

```bash
rm -f ~/.pi/agent/alibaba-config.json ~/.pi/agent/alibaba-models.cache.json \
      ~/.pi/agent/alibaba-catalog.lock* \
      ~/.pi/agent/alibaba-plan-models.cache.json \
      ~/.pi/agent/alibaba-cloud-models.cache*.json  # last glob: 1.4.x leftover
# then remove the "alibaba-plan" / "alibaba-cloud" entries from ~/.pi/agent/auth.json
# and drop any "alibaba-*/…" ids from enabledModels in ~/.pi/agent/settings.json
```

> Or, from inside a session, `/alibaba → Reset all` wipes config, both auth entries, the plan-model
> cache and `alibaba-*` entries in `enabledModels` in one step.

Finally confirm only one copy is configured:

```bash
pi list
```

---

## 5. Start Pi

Launch Pi by running:

```bash
pi
```

This starts the interactive coding agent session.

---

## 6. Configure Alibaba Cloud Domain

> **Skip this step** if you are using the default International endpoint (`dashscope-intl.aliyuncs.com`).

Within the Pi session, run:

```
/alibaba
```

Select **Cloud — Change Domain**. The fork offers four shared hosts, five workspace-domain builders,
and a free-text Custom entry:

| Option | Domain |
|---|---|
| International | `dashscope-intl.aliyuncs.com` (default — Singapore) |
| China | `dashscope.aliyuncs.com` (Beijing) |
| US — Virginia | `dashscope-us.aliyuncs.com` |
| Hong Kong | `cn-hongkong.dashscope.aliyuncs.com` |
| Workspace — Beijing / Singapore / Tokyo / Frankfurt / US | `{WorkspaceId}.{region}.maas.aliyuncs.com` — you paste only your business-space ID and the menu builds the host |
| Custom | *(paste your own)* |

Workspace regions are `cn-beijing`, `ap-southeast-1`, `ap-northeast-1`, `eu-central-1`, `us-east-1`.
Alibaba recommends workspace domains, and they are **required** for Tokyo and Frankfurt (those regions
have no shared host).

> **Hong Kong workspace hosts.** `cn-hongkong` is *not* one of the fork's workspace regions, so a
> `{WorkspaceId}.cn-hongkong.maas.aliyuncs.com` endpoint has to be entered through **Custom** — the menu
> will not build it for you, and the workspace auto-upgrade below never touches it (nor any Custom host).
> This is exactly the case for an existing `…​.cn-hongkong.maas.aliyuncs.com` config: it survives the
> migration untouched and is read as a custom, key-independent domain.

### Auto workspace-domain upgrade

When the Cloud domain is one of the three shared regional hosts, the extension reads the WorkspaceId
bound to your key from `GET /api/v1/models/limits`, probes `{WorkspaceId}.{region}.maas.aliyuncs.com`,
and **only on a successful probe** switches the config to the workspace host. A failed probe changes
nothing and retries at most once per 24 h. Manage it with **Cloud — Auto workspace domain**
(detect now / enable / disable); picking a shared host explicitly in the menu counts as "stay here" and
disables it. `/alibaba → Status` shows `Auto-WS` and the discovered WorkspaceId.

### API format

The fork defaults Cloud to **OpenAI Responses** (`/compatible-mode/v1/responses`). The format is pinned
into `alibaba-config.json` on first boot, so an existing `"cloudApiFormat": "anthropic-messages"` entry
(stale npm-era value) is **kept** rather than silently flipped. To move onto Responses:

```
/alibaba → Cloud — Change API Format → OpenAI Responses
```

Per-model fallbacks stay automatic: a family whose capability row is not Responses-capable is routed to
Chat Completions on its own (`kimi-k2.x`, `MiniMax-M2.5`, `glm-4.5`, bare `glm-5`/`glm-5.1`, and older
DeepSeek/GLM/Kimi/MiniMax releases). 2.0.0 raised DeepSeek V4/V4.1, GLM-5.2/5.3, MiniMax-M2.1 and
Kimi K3 onto Responses, so the set is much smaller than the 1.5.x release notes suggest — measured
against this workspace's 26-id catalogue, **only `kimi-k2.7-code` falls back**. `/alibaba → Status`
reports how many models fall back. With Responses active, requests carry
`x-dashscope-session-cache: enable` — toggle it with **Cloud — Session Cache: On / Off** if your usage
is one-shot-heavy (cache writes bill at 125 % of input, reads come back at ~10 %).

> **Measured on this setup (2026-10-04, `openai-responses`, Hong Kong workspace domain, thinking
> `high`, `qwen3.8-flash`):** a forced ~2,000-word answer completed with `stopReason: stop` at **5,920
> output tokens** (10,246 characters of thinking, nothing truncated), and a third turn in the same
> session read `cacheRead: 11,436` of a 11,718-token prompt (~97 %). The first follow-up turn can still
> show `cacheRead: 0` while the server-side session cache warms up, so judge the cache over three turns
> rather than two.
>
> **The truncation fix does not depend on this format switch.** The fork's real catalogue
> `max_output_tokens` (131,072) leaves enough answer room even on `anthropic-messages` — measured there
> too: 4,858 output tokens, `stopReason: stop`. Responses is preferred because thinking and the answer
> do not share one `max_tokens` budget at all, and because session-cache reads are cheaper than the
> implicit Anthropic-path cache.

Other entries in the same menu: `Status`, `Refresh model lists`, `Re-login Plan` / `Re-login Cloud`,
`Plan — Change Endpoints`, `Tools — Exposure`, `Tools — Sidecar model`, `Image — Default model`,
`Rate limits (Cloud)`, `Cloud — Authorized-only Filter`, `Context Window — Override`, `Reset all`.

---

## 7. Login with an Alibaba API Key

```
/login
```

Pick the entry matching your account type — there is **no "Alibaba Hong Kong" provider**; the region is
a Cloud *domain* setting (step 6), not a provider:

| Account | `/login` section | Provider entry | Provider id | Token shape |
|---|---|---|---|---|
| Pay-per-token DashScope | **Use an API key** | Alibaba Cloud (API Key) | `alibaba-cloud` | `sk-…` |
| Model Studio Coding Plan subscription | **Plans** | Alibaba Model Studio Coding Plan | `alibaba-plan` | `sk-sp-…` / `sk-tok-…` |

Both providers register side by side, so you can switch per chat from the model picker.

> **Cloud without `/login`:** the Cloud provider also reads the `DASHSCOPE_API_KEY` environment
> variable. If it is set, the live catalogue is fetched from it on startup and no login step is needed.

> **Pasted the wrong token shape?** The login validators catch it and offer to redirect you. To redo a
> provider manually: `/alibaba → Re-login Cloud` (or `Re-login Plan`), then `/login` again.

Replacing the Cloud key **re-derives the endpoint from scratch** (shared default first, then the new
key's own workspace domain), so a stale workspace host can no longer `403` a fresh key. Use
`Re-login Cloud` to clear the key binding and force that re-derivation immediately.

---

## 8. Configure Scoped Models

Enable the Alibaba models used for model cycling:

```
/scoped-models
```

The fork serves a **live catalogue**, so model ids come from Alibaba rather than from a list baked into
the package. Confirm real ids before editing settings by hand:

```bash
pi --offline --list-models alibaba-cloud     # cached snapshot, zero network
```

The three enabled models for this setup (stored as `enabledModels` in `~/.pi/agent/settings.json`):

| Model | Setting entry |
|-------|---------------|
| Qwen 3.8 Flash | `alibaba-cloud/qwen3.8-flash` |
| Qwen 3.8 Max | `alibaba-cloud/qwen3.8-max` |
| Qwen 3.7 Plus | `alibaba-cloud/qwen3.7-plus` |

These are what `Ctrl+P` cycles through. The provider id prefix (`alibaba-cloud/`) is unchanged from the
npm package, so existing `enabledModels` entries carry over — but a stale id left in `enabledModels` can
now be pruned automatically by `/alibaba → Reset all`, and new catalogue ids (`qwen3.6-*`, DeepSeek V4,
Kimi K2.6, GLM-5, MiniMax M2.5, …) are available without any extension update.

If a newly shipped model does not appear:

```
/alibaba → Refresh model lists
```

---

## 9. Optional: DashScope Sidecar And Image Tools

The fork registers two extra tools, each with its own **exposure** (`/alibaba → Tools — Exposure`):

| Exposure | Meaning |
|---|---|
| `codemode` (default) | callable from `codemode` scripts under the `alibaba` namespace; **not** declared to the model every turn |
| `direct` | declared to the model on every turn (the old npm behaviour for `alibaba_tools`) |
| `deferred` | reachable through `tool_search` instead |
| `off` | not registered at all |

| Tool | What it does |
|---|---|
| `alibaba_tools` | one tool for live web search, page extract, code interpreter, image search. Cloud key required; billed separately. |
| `alibaba_image` | DashScope image generation/editing with every generation parameter (`model`, `size`, `n`, `seed`, `negative_prompt`, `prompt_extend`, `save`, …). Cloud only — Plan accounts register no image models. |

Because the 2.0.0 default changed from `direct` to `codemode`, a setup that wants the model to call the
sidecar directly must set it explicitly:

```
/alibaba → Tools — Exposure → alibaba_tools → direct
```

With both tools left at `codemode` and `codemode` disabled in Pi, neither is reachable and the only
generation path is `/alibaba image <prompt>`.

```text
/alibaba image a red fox in the snow --model qwen-image-max --size 1664*928 --save fox.png
```

---

## 10. Configure Web Search with Exa

Add the Exa API key to your shell configuration:

```bash
cat << 'EOF' >> ~/.bashrc

export EXA_API_KEY="exa-your-actual-exa-key"
EOF
```

Then install the web access extension:

```bash
pi install npm:pi-web-access
```

Restart Pi for the extension to load its tools. The `EXA_API_KEY` environment variable will enable
Exa-powered web search.

> **Note:** `/reload` may not be sufficient — start a new session for the extension tools to register
> properly.
>
> **Overlap:** the Alibaba fork ships its own web search (`alibaba_tools`), billed on the DashScope
> sidecar. Keep Exa if you want provider-independent search; drop `pi-web-access` if you would rather
> pay for one search path only.

---

## 11. Install the Ask-User-Question Extension

Install the `ask_user_question` tool extension:

```bash
pi install npm:@juicesharp/rpiv-ask-user-question
```

This gives the model a structured way to ask clarifying questions during a task: a terminal dialog with
up to four questions and selectable options. The model calls it when instructions are ambiguous instead
of guessing. No configuration needed — restart the session after installing.

---

## 12. Set Up OpenSpec for Spec-Driven Planning

Install OpenSpec globally (requires Node.js 20.19.0+; Pi bundles a compatible Node on PATH):

```bash
npm install -g @fission-ai/openspec@latest
```

From the project root, initialise OpenSpec for Pi:

```bash
openspec init --tools pi --no-animation
```

This writes six Pi slash commands under `.pi/prompts/opsx-*.md` and six matching skills under
`.pi/skills/openspec-*/SKILL.md` — `explore`, `propose`, `apply`, `update`, `sync`, `archive`.

Then edit the generated `openspec/config.yaml` and replace the commented-out `context:` placeholder with
a short project description so proposals fit this docs-only repo.

```yaml
schema: spec-driven

context: |
  This repo documents how to install and configure the Pi coding agent.
  It is mostly Markdown (no build/test pipeline); the "code" being changed
  is documentation, config snippets, and Pi extensions/skills under .pi/.
  Keep proposals scoped to docs under .pi/ skills, prompt templates, and
  Markdown guides. Never assume a package manager or CI exists here.
```

See [`GREENFIELD_GUIDE.md`](./GREENFIELD_GUIDE.md) for the umbrella-change workflow used to start a
project from nothing with OpenSpec.

---

## 13. Frontend Visual Loop: Browser Screenshots The Model Can See

Pi can only fix a layout it can see. This setup gives the model a real browser whose screenshots
arrive as **image content inside the tool result**, so after editing a component it looks at the
rendered page instead of guessing from source. Pi's tool contract already allows it —
`AgentToolResult.content` is `(TextContent | ImageContent)[]`, documented as "Text or image content
returned to the model" — so this is a supported path, not a workaround.

Two pieces, one for capability and one for judgement:

| Piece | Contributes |
|---|---|
| `pi-agent-browser-native` | the `agent_browser` tool — drives the `agent-browser` CLI and attaches screenshots inline |
| `frontend-visual-loop` skill | when to capture, which viewports, and the WSL traps |

### Install the CLI on the Linux side

```bash
npm install -g agent-browser
agent-browser install --with-deps
```

> **Install inside WSL, not through Windows npm.** A `/mnt/c/...` install runs the CLI over interop
> while Chrome for Testing runs natively, so relative paths resolve against the long-lived daemon's
> launch directory and screenshots land in the wrong folder. Confirm with
> `which -a agent-browser` — the `~/.local/share/pi-node/...` entry must come first.

`agent-browser install --with-deps` downloads Chrome for Testing to `~/.agent-browser/browsers/` and
installs the Linux system libraries it needs. It runs headless (`--headless=new` with SwiftShader),
so no display server is involved.

### Install the Pi package

```bash
pi install npm:pi-agent-browser-native
pi list
```

The wrapper enforces an upstream CLI floor of **0.35.0** (target **0.38.1**) and refuses to run
against older CLIs. On this machine the first package call auto-upgraded 0.27.0 → 0.38.1.

> **Version note.** On Node 22 npm resolves **0.7.1**, not the latest 0.9.x, because 0.9 declares
> `engines.node >=24.21.0`. 0.7.1 has the same inline-image attachment, so the visual loop works
> unchanged; upgrade Node past 24.21 only if you want the newer wrapper.

### Tools

| Tool | Notes |
|---|---|
| `agent_browser` | main entry. `args` are 1:1 with the CLI (`open`, `screenshot`, `snapshot -i`, `set viewport`, `console`, `errors`, `eval`, `diff`, `vitals`, …). Use `batch` to fold a whole checkpoint into one call |
| `agent_browser_code` | bounded JavaScript over the same browser for loops and branches. Limits: 25 calls, 120 s default, ≤8 images / 20 MiB total, 5 MiB per image |
| `agent_browser_tools` | lists and enables the specialized tools (`agent_browser_action`, `_qa`, `_electron`, `_source`, `_network_source`). Inactive until enabled |
| `agent_browser_web_search` | appears only when an Exa or Brave key resolves — already satisfied by [step 10](#10-configure-web-search-with-exa). Prefer it over automating Google, which serves CAPTCHAs to headless Chrome |

### The skill

Tracked in this repo at [`personal-skills/frontend-visual-loop/`](./personal-skills/README.md) and
symlinked into the personal skills directory, so it stays personal-scope (following you into every
frontend repo) while remaining version-controlled with the repo as the single source of truth:

```bash
ln -s "$PWD/personal-skills/frontend-visual-loop" ~/.pi/agent/skills/frontend-visual-loop
```

Pi's loader follows symlinked skill directories, so no copy or sync step is needed and the bundled
script keeps its executable bit. It auto-triggers on UI edits and phrasing like
"looks wrong", "is invisible", "check the page", "responsive check", and can be forced with
`/skill:frontend-visual-loop`. It encodes:

- screenshot **before** editing to confirm the symptom, and **after** to confirm the fix
- a 390×844 / 768×1024 / 1280×800 viewport matrix — desktop-only checks miss the common defects
- `console` + `errors --json` alongside every capture, because a page can look fine and still throw
- absolute artifact paths, and closing the browser at the end
- `scripts/viewport-sweep.sh` for a three-viewport capture in one command

> **Screenshots are not free.** Images stay in the transcript and are re-sent on every later request,
> so the skill captures at decision points rather than after each edit. There is deliberately no
> auto-screenshot hook on `tool_call`; if you want one, pair it with a `context` handler that drops
> stale images first.

### Gotchas verified on this machine

| Symptom | Cause / fix |
|---|---|
| All-white screenshot that looks like a broken app | Stale `agent-browser` daemons (left from a deleted cwd, or a Windows-side copy) split `open` and `screenshot` across browsers. Confirm with `get url` after `open`; recover with `agent-browser close --all`, `pkill -f 'agent-[b]rowser-linux'`, then `agent-browser doctor` |
| `[agent-browser] launched browser` repeats on every call | Same cause — sessions are not being reused |
| Screenshot written to the repo root instead of the target dir | CLI running over Windows interop; reinstall on the Linux side |
| `errors` prints a bare `✗` | Plain formatter drops multi-line stacks. Add `--json` |
| Google/httpbin return a consent wall | Expected anti-bot response from headless Chrome. Local dev servers are unaffected |
| Model describes nothing although a screenshot was returned | Vision must be enabled. `models-store.json` lists `qwen3.8-flash` as `input: ["text","image"]`, but `alibaba-cloud-models.cache.json` says `["text"]`; the store wins. If images stop being read, check the active model's `input` array |

---

## 14. Update / Uninstall The Alibaba Extension

`pi update` re-fetches the git source:

```bash
pi update git:github.com/RarogCmex/pi-alibaba-models
```

> **`pi remove` does not clean extension-private state** — auth entries, `alibaba-config.json`, catalog
> caches and `alibaba-*` ids in `enabledModels` all survive it. For a clean uninstall:

```text
1. /alibaba  →  "Reset all"   (wipes config, both auth entries, plan-models cache, alibaba-* enabledModels)
2. pi remove git:github.com/RarogCmex/pi-alibaba-models
```

The fork's own state files (all under `~/.pi/agent`, or `$PI_CODING_AGENT_DIR`):

| Path | Purpose |
|---|---|
| `auth.json` | both provider credentials (0600) — shared with Pi, delete only the `alibaba-plan` / `alibaba-cloud` keys |
| `alibaba-config.json` | domain, API format, toggles, exposure, key fingerprint, catalog fetch timestamps |
| `alibaba-models.cache.json` | versioned catalog snapshot used to seed boot with zero network |
| `alibaba-catalog.lock` | transient fetch lock |
| `models-store.json` | Pi-owned, shared across providers — the extension's rows there are a bonus channel |

---

## Git Push Auth Under WSL

WSL keeps its own git config and has no credentials of its own, so the first `git push` fails with:

```text
fatal: could not read Username for 'https://github.com': No such device or address
```

Rather than maintaining a second set of keys, let WSL borrow the credentials Git for Windows already
stores. One login on either side then covers both.

### Prerequisites (all on the Windows side)

This only works if Windows is configured to hand credentials to Git Credential Manager. Four things
must be true:

| # | Requirement | Check from WSL |
|---|---|---|
| 1 | Git for Windows installed (it bundles GCM) | `ls "/mnt/c/Program Files/Git"` |
| 2 | GCM set as the Windows credential helper — written by the Git for Windows installer, or by `git-credential-manager.exe configure` | `grep -A1 '^\[credential\]' "/mnt/c/Program Files/Git/etc/gitconfig"` → `helper = manager` |
| 3 | A GitHub account already signed in on Windows | `"/mnt/c/Program Files/Git/mingw64/bin/git-credential-manager.exe" github list` prints your login |
| 4 | WSL interop enabled, so `.exe` files can run | `ls /proc/sys/fs/binfmt_misc/WSLInterop`, and no `[interop] enabled=false` in `/etc/wsl.conf` |

> **Row 3 is the one people are missing.** If `github list` prints nothing, seed it **from Windows**:
> run `git-credential-manager github login` in PowerShell, or simply `git push` once from Git Bash and
> finish the browser sign-in. GCM then stores the token in **Windows Credential Manager**, visible as
> `git:https://github.com` under `cmdkey /list`, and that vault is what WSL reads afterwards. Nothing
> needs to be signed into from inside WSL.

### Configure WSL

```bash
git config --global credential.helper \
  '!"/mnt/c/Program Files/Git/mingw64/bin/git-credential-manager.exe"'
```

> **The `!` prefix is not optional.** It tells git to run the value through a shell, which is what lets
> the space in `Program Files` parse. A bare path is split on the first space and fails. Adjust the
> path if Git lives elsewhere (Scoop, a custom install dir).

### Verify

```bash
GIT_TERMINAL_PROMPT=0 git ls-remote origin refs/heads/main
```

`GIT_TERMINAL_PROMPT=0` forbids any interactive fallback, so a successful run proves the credential
came from GCM rather than from a prompt you did not notice. Drop the variable once it works.

### If it stops working

| Symptom | Cause / fix |
|---|---|
| `No such device or address` returns | Helper unset, or the GCM path moved. Re-check with `ls "/mnt/c/Program Files/Git/mingw64/bin/git-credential-manager.exe"` |
| `git-credential-manager.exe github list` prints nothing | The Windows-side credential is gone (logout, vault cleanup, token revocation). Re-run `github login` on Windows |
| A browser sign-in window opens on every push | Expired token. Complete the flow once; GCM re-caches it |
| `git-credential-manager.exe: command not found` or exec error | Interop disabled. Check `/etc/wsl.conf` for `[interop] enabled=false`, then `wsl --shutdown` from Windows |
| Push works from Windows but not WSL, no error | Windows git and WSL git are separate installs with separate configs — this section configures only the WSL one |

> **Scope note.** This lets WSL git read your Windows credential vault for every HTTPS git operation,
> including the `git clone` that Pi itself shells out to for `pi install git:…` sources, so a private
> git-hosted package installs without further setup. That convenience crosses the WSL/Windows boundary:
> if you want the two environments isolated, skip this and use a dedicated SSH key in `~/.ssh` instead
> (`git config --global --unset credential.helper` to back it out).

---

## Troubleshooting The Swap

| Symptom | Cause / fix |
|---|---|
| `pi-alibaba-models is installed 2 times; 1 of those would shadow this copy` | npm copy and git copy both configured. Run `pi remove` naming the copy in the error (usually `npm:pi-alibaba-models`) and restart. `PI_ALIBABA_ALLOW_DUPLICATE=1` boots anyway (only useful when comparing versions deliberately). |
| Long replies cut off mid-sentence, `stopReason: length` (and, downstream, `Context overflow recovery failed: Summarization failed: generation hit the token cap…` at a nearly empty context) | The classic npm-1.1.1 symptom: its hardcoded card `maxTokens: 8192` is split by pi's Anthropic path between thinking (7,168) and answer (~1,024), so anything longer stops with `length`. Because `isRecoverableLength()` only checks `output < maxTokens`, pi misreads that as context pressure and runs overflow recovery — whose summary call gets the same ~1,024-token answer room and fails too. Fix: install the fork (real `max_output_tokens`). Moving Cloud to `openai-responses` helps further, since thinking and answer then share no budget at all. |
| Every request returns `403` after changing the API key | Old behaviour: endpoint inherited from the previous key. The fork re-derives it; run `/alibaba → Re-login Cloud` then `/login`. |
| `/alibaba` command missing | `pi list` shows the package? If not, reinstall and restart Pi in a new session. |
| Model picker shows "No matching models" | Not logged in yet — models register only after a successful Cloud/Plan login (or with `$DASHSCOPE_API_KEY` set). |
| New model not listed | `/alibaba → Refresh model lists` (force, always fetches). |
| Wrong context window on a brand-new model | `/alibaba → Context Window — Override` (per model, or `*` for all). |
| `429 InternalError.Algo … Too many requests` / `Backend buffer overflow` | DashScope wraps rate limits inside a 200 SSE error event; chat auto-retries, `alibaba_tools` retries in the tool card. RPM windows reset in ~60 s; check `/alibaba → Rate limits (Cloud)`. |
| `alibaba_tools` missing | Exposure is `off` — `/alibaba → Tools — Exposure → alibaba_tools → codemode` (or `direct`), then restart. Needs a Cloud key. |

---

## Project-Local And Personal Skills

This repository also ships three hand-written skills under `.pi/skills/`. Pi loads them automatically
when you work in this project, so there is no install step. (OpenSpec writes six generated skills into
the same directory — see [step 12](#12-set-up-openspec-for-spec-driven-planning).)

- **asd-ste100** — writing and rewriting human-facing docs in clear, simple English: a README,
  changelog, setup guide, tutorial, release note, or user guide. It keeps numbers, commands, paths,
  and links unchanged. The rules are ASD-STE100-inspired; the skill claims no certified compliance
  and ships no approved-word dictionary
- **pi-extension-authoring** — designing, writing, and debugging Pi extensions
- **pi-skill-authoring** — authoring and reviewing Agent Skills (SKILL.md files)

Pi loads a skill when the task matches its description. Force one with `/skill:asd-ste100`. Run
`/reload` after you edit a skill during an active session.

Personal skills load in every project. They are tracked under
[`personal-skills/`](./personal-skills/README.md) and symlinked into `~/.pi/agent/skills/`:

- **frontend-visual-loop** — browser screenshots the model can see during frontend work
  ([step 13](#13-frontend-visual-loop-browser-screenshots-the-model-can-see)). Copy it into
  `.pi/skills/` instead to scope it to one repo — not both, since a name collision keeps the
  first-discovered copy and warns on every start.

---

## Summary

| Step | Command / Action | Purpose |
|------|-----------------|---------|
| 1 | `curl -fsSL https://pi.dev/install.sh \| sh` | Install Pi CLI (needs >= 1.0.0 for the fork) |
| 2 | Add `export PATH="$HOME/.local/share/pi-node/current/bin:$PATH"` to `~/.bashrc` | Make Pi's bundled Node the default node/npm (see step 2) |
| 3 | `pi install git:github.com/RarogCmex/pi-alibaba-models` | Add Alibaba model support (fork; no npm release) |
| 4 | `pi remove npm:pi-alibaba-models` | Drop the stale npm copy so the guard doesn't block boot |
| 5 | `pi` | Start Pi coding agent (new session, not `/reload`) |
| 6 | `/alibaba` → **Cloud — Change Domain** → International / China / US / Hong Kong / workspace / Custom | Set the Cloud endpoint (optional) |
| 7 | `/login` → **Use an API key → Alibaba Cloud (API Key)**, or **Plans → Alibaba Model Studio Coding Plan** | Authenticate |
| 8 | `/scoped-models` → `qwen3.8-flash`, `qwen3.8-max`, `qwen3.7-plus` | Configure scoped models |
| 9 | `/alibaba` → **Tools — Exposure** / **Cloud — Change API Format** | Opt into sidecar tools, image tools, Responses format |
| 10 | Add `EXA_API_KEY` to `~/.bashrc` + `pi install npm:pi-web-access` | Configure web search with Exa |
| 11 | `pi install npm:@juicesharp/rpiv-ask-user-question` | Install ask-user-question tool |
| 12 | `npm install -g @fission-ai/openspec@latest` → `openspec init --tools pi --no-animation` → edit `openspec/config.yaml` `context:` block | Add spec-driven planning (`/opsx-propose` → `/opsx-apply` → `/opsx-archive`) |
| 13 | `npm install -g agent-browser` + `agent-browser install --with-deps` + `pi install npm:pi-agent-browser-native` + symlink `personal-skills/frontend-visual-loop` into `~/.pi/agent/skills/` | Let the model see rendered UI while fixing frontends |
| 14 | `pi update git:github.com/RarogCmex/pi-alibaba-models` | Keep the fork current |

---

*Last updated: 2026-10-28 — listed the `asd-ste100` skill in
[Project-Local And Personal Skills](#project-local-and-personal-skills), which took the hand-written
count from two to three. The description was read from `.pi/skills/asd-ste100/SKILL.md` on this
machine, and the skill was confirmed present in Pi's startup skill list for this project.*

*Earlier (2026-10-04) — added [step 13](#13-frontend-visual-loop-browser-screenshots-the-model-can-see)
(frontend visual loop: `agent-browser` + `pi-agent-browser-native` + `frontend-visual-loop` skill, now
tracked under `personal-skills/`), the untracked-but-verified
[Git Push Auth Under WSL](#git-push-auth-under-wsl) section, and the new
[Node.js And npm Under WSL](#2-nodejs-and-npm-under-wsl) step 2 (which renumbered the Alibaba
update/uninstall section to 14). Its claims were checked against the installed
wrapper source (0.7.1: `MINIMUM_AGENT_BROWSER_VERSION` 0.35.0, target 0.38.1, inline attachment in
`lib/results/presentation/artifacts.js`, tool list and `agent_browser_code` limits from its README) and
against live `pi -p` runs on `qwen3.8-flash` under WSL2/Ubuntu 24.04, including an end-to-end test where
a planted low-contrast bug was diagnosed from a screenshot and verified fixed. The git-auth section's
prerequisites, GCM 2.9.0 command names, and the `pi install git:` clone path were each re-checked against
`/mnt/c/Program Files/Git/etc/gitconfig`, `git-credential-manager --help`, `cmdkey /list`, and
`package-manager.js` on this machine.*

*Earlier — Alibaba provider switched from `npm:pi-alibaba-models` (upstream 1.1.1) to the
maintained fork [`RarogCmex/pi-alibaba-models`](https://github.com/RarogCmex/pi-alibaba-models) 2.0.0,
with Cloud set to `openai-responses`. Menu labels, domain/workspace options, capability table and state
file names below were re-checked against the installed fork source and `pi --offline --list-models`, and
the truncation and session-cache claims against live `pi -p --mode json` runs on `qwen3.8-flash` with
thinking `high`.*
