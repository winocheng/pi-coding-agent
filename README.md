# Pi Coding Agent Setup Documentation

This repository documents the setup steps for configuring the Pi coding agent.

It is a personal reference, not an official guide. It records one working setup on
**WSL2 (Ubuntu 24.04) on a Windows host**, using **Alibaba Cloud (Qwen) models** through
DashScope.

Following the guide sets up:

- The Pi CLI and its bundled Node.js under WSL2
- Alibaba Cloud model access through the `pi-alibaba-models` fork
- Web search with Exa (`pi-web-access`) and the ask-user-question extension
- Browser screenshots the model can see (`agent-browser` + `pi-agent-browser-native`)
- Project skills under `.pi/skills/` and personal skills under `personal-skills/`
- OpenSpec for spec-driven planning

The main configuration guide is available in [`CONFIGURATION_GUIDE.md`](./CONFIGURATION_GUIDE.md).
For starting a new project from scratch, see [`GREENFIELD_GUIDE.md`](./GREENFIELD_GUIDE.md).
