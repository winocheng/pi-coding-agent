# Pi Coding Agent — Configuration Guide

This document walks through the full setup process for configuring the Pi coding agent with Alibaba Cloud models.

---

## Table of Contents

1. [Install Pi](#1-install-pi)
2. [Install the Alibaba Models Extension](#2-install-the-alibaba-models-extension)
3. [Start Pi](#3-start-pi)
4. [Configure Alibaba Cloud Domain](#4-configure-alibaba-cloud-domain)  
   *Optional — skip if using the default International endpoint*
5. [Login with Alibaba Hong Kong API Key](#5-login-with-alibaba-hong-kong-api-key)
6. [Configure Scoped Models](#6-configure-scoped-models)
7. [Configure Web Search with Exa](#7-configure-web-search-with-exa)
8. [Install the Ask-User-Question Extension](#8-install-the-ask-user-question-extension)
9. [Set Up OpenSpec for Spec-Driven Planning](#9-set-up-openspec-for-spec-driven-planning)

---

## 1. Install Pi

Download and run the official installer script:

```bash
curl -fsSL https://pi.dev/install.sh | sh
```

This installs the Pi coding agent CLI to your system.

---

## 2. Install the Alibaba Models Extension

Install the `pi-alibaba-models` extension package via npm:

```bash
pi install npm:pi-alibaba-models
```

This adds support for Alibaba Cloud (DashScope) models to Pi.

---

## 3. Start Pi

Launch Pi by running:

```bash
pi
```

This starts the interactive coding agent session.

---

## 4. Configure Alibaba Cloud Domain (Optional)

> **Skip this step** if you are using the default International endpoint (`dashscope-intl.aliyuncs.com`).
>
> This step is only needed if you want to switch to the **China** endpoint or a **Custom** workspace domain.

Within the Pi session, run the Alibaba configuration command:

```
/alibaba
```

From the interactive menu, select **Cloud — Change Domain**. You will be presented with three options:

| Option        | Domain                                         | Notes                                |
|---------------|------------------------------------------------|--------------------------------------|
| International | `dashscope-intl.aliyuncs.com`                  | Default — Singapore region           |
| China         | `dashscope.aliyuncs.com`                       | Mainland China endpoint              |
| Custom        | *(paste your own)*                             | For workspace-specific domains       |

If you select **Custom**, enter your domain in the following format:

```
{your-workspace-id}.cn-hongkong.maas.aliyuncs.com
```

> **Note:** Replace `{your-workspace-id}` with your actual Alibaba Cloud workspace ID. The `cn-hongkong` region routes your requests through the Hong Kong endpoint.

You can also use this menu later to switch API format (Anthropic-compat vs OpenAI-compat), refresh model lists, or reset all state.

---

## 5. Login with Alibaba Hong Kong API Key

Authenticate with your Alibaba Cloud API key:

```
/login
```

Select the **Alibaba Hong Kong** provider and enter your API key when prompted.

---

## 6. Configure Scoped Models

Enable the Alibaba models used for model cycling:

```
/scoped-models
```

The three enabled models (stored as `enabledModels` in `~/.pi/agent/settings.json`):

| Model | Setting entry |
|-------|---------------|
| Qwen 3.8 Flash | `alibaba-cloud/qwen3.8-flash` |
| Qwen 3.8 Max | `alibaba-cloud/qwen3.8-max` |
| Qwen 3.7 Plus | `alibaba-cloud/qwen3.7-plus` |

These are what `Ctrl+P` cycles through.

## 7. Configure Web Search with Exa

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

Restart Pi for the extension to load its tools. The `EXA_API_KEY` environment variable will enable Exa-powered web search.

> **Note:** `/reload` may not be sufficient — start a new session for the extension tools to register properly.

---

## 8. Install the Ask-User-Question Extension

Install the `ask_user_question` tool extension:

```bash
pi install npm:@juicesharp/rpiv-ask-user-question
```

This gives the model a structured way to ask clarifying questions during a task: a terminal dialog with up to four questions and selectable options. The model calls it when instructions are ambiguous instead of guessing. No configuration needed — restart the session after installing.

---

## 9. Set Up OpenSpec for Spec-Driven Planning

Install OpenSpec globally (requires Node.js 20.19.0+; Pi bundles a compatible Node on PATH):

```bash
npm install -g @fission-ai/openspec@latest
```

From the project root, initialise OpenSpec for Pi:

```bash
openspec init --tools pi --no-animation
```

This writes six Pi slash commands under `.pi/prompts/opsx-*.md` and six matching skills under `.pi/skills/openspec-*/SKILL.md` — `explore`, `propose`, `apply`, `update`, `sync`, `archive`.

Then edit the generated `openspec/config.yaml` and replace the commented-out `context:` placeholder with a short project description so proposals fit this docs-only repo:

```yaml
schema: spec-driven

context: |
  This repo documents how to install and configure the Pi coding agent.
  It is mostly Markdown (no build/test pipeline); the "code" being changed
  is documentation, config snippets, and Pi extensions/skills under .pi/.
  Keep proposals scoped to docs under .pi/ skills, prompt templates, and
  Markdown guides. Never assume a package manager or CI exists here.
```

See `OPENSPEC_GUIDE.md` for the full workflow.

---

## Project-Local Skills

This repository also ships two skills under `.pi/skills/`, loaded automatically when working in this project (no install step):

- **pi-extension-authoring** — designing, writing, and debugging Pi extensions
- **pi-skill-authoring** — authoring and reviewing Agent Skills (SKILL.md files)

---

## Summary

| Step | Command / Action | Purpose |
|------|-----------------|---------|
| 1 | `curl -fsSL https://pi.dev/install.sh \| sh` | Install Pi CLI |
| 2 | `pi install npm:pi-alibaba-models` | Add Alibaba model support |
| 3 | `pi` | Start Pi coding agent |
| 4 | `/alibaba` → **Cloud — Change Domain** → Custom → `{workspace-id}.cn-hongkong.maas.aliyuncs.com` | Set custom API domain (optional) |
| 5 | `/login` with Alibaba HK API key | Authenticate |
| 6 | `/scoped-models` → `qwen3.8-flash`, `qwen3.8-max`, `qwen3.7-plus` | Configure scoped models |
| 7 | Add `EXA_API_KEY` to `~/.bashrc` + `pi install npm:pi-web-access` | Configure web search with Exa |
| 8 | `pi install npm:@juicesharp/rpiv-ask-user-question` | Install ask-user-question tool |
| 9 | `npm install -g @fission-ai/openspec@latest` → `openspec init --tools pi --no-animation` → edit `openspec/config.yaml` `context:` block | Add spec-driven planning (`/opsx-propose` → `/opsx-apply` → `/opsx-archive`) |

---

*Last updated: 2026-10-01*
