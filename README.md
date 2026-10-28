# Pi Coding Agent Setup Documentation

This repository holds setup guides for the Pi coding agent.

It is a personal reference, not official documentation. Each guide records one working setup on this
machine: **WSL2 (Ubuntu 24.04) on a Windows host**, with **Alibaba Cloud (Qwen) models** through
DashScope.

The configuration guide sets up:

- The Pi CLI and its bundled Node.js under WSL2
- Alibaba Cloud model access through the `pi-alibaba-models` fork
- Web search with Exa (`pi-web-access`) and the ask-user-question extension
- Browser screenshots the model can see (`agent-browser` and `pi-agent-browser-native`)
- Project skills under `.pi/skills/` and personal skills under `personal-skills/`
- OpenSpec for spec-driven planning

Read [`CONFIGURATION_GUIDE.md`](./CONFIGURATION_GUIDE.md) for the full setup. Read
[`GREENFIELD_GUIDE.md`](./GREENFIELD_GUIDE.md) to start a new project from scratch.
