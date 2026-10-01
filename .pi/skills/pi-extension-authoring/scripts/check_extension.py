#!/usr/bin/env python3
"""Preflight checker for Pi extensions (heuristic, static — not a type checker).

Usage:
    python3 check_extension.py <ext.ts|ext-dir> [...]

Checks each extension file for the mistakes that most often break Pi extensions:
  - missing default export factory
  - side effects at module scope (timers, sockets, processes, watchers)
  - dialogs without a ctx.hasUI guard / custom UI without a mode === "tui" guard
  - `continue: true` boundary results (loop risk) — reminds you to verify the guard
  - leftover console.log debugging
  - for package dirs: package.json sanity (pi-package keyword, pi manifest paths exist)

The real load test is:  pi --extension <file>   (watch startup diagnostics).
Exit code 0 = no errors (warnings allowed), 1 = at least one error, 2 = usage error.
"""

from __future__ import annotations

import json
import os
import re
import sys

# Calls that start something long-lived; at module scope (column 0) they are errors
# because some invocations load extensions without starting a session.
SIDE_EFFECT_RE = re.compile(
    r"\b(spawn|execFile|exec|fork)\s*\(|setInterval\s*\(|setTimeout\s*\(|setImmediate\s*\("
    r"|\.listen\s*\(|createServer\s*\(|new\s+WebSocket|\.watch\s*\(|watchFile\s*\("
)
DIALOG_RE = re.compile(r"\bctx\.ui\.(confirm|select|prompt)\s*\(|\bui\.(confirm|select|prompt)\s*\(")
CUSTOM_UI_RE = re.compile(r"\bctx\.ui\.(custom|setWidget|setFooter|setHeader|setEditorComponent)\s*\(")
TUI_GUARD_RE = re.compile(r'mode\s*===?\s*["\']tui["\']|hasUI')
HASUI_GUARD_RE = re.compile(r"\bhasUI\b")
CONTINUE_RE = re.compile(r"continue\s*:\s*true")
CONSOLE_RE = re.compile(r"\bconsole\.(log|debug)\s*\(")
DEFAULT_EXPORT_RE = re.compile(r"export\s+default\s+(async\s+)?(function|\(|[A-Za-z_$])")
EXT_API_RE = re.compile(r"\bExtensionAPI\b")
CODE_FENCE_RE = re.compile(r"^\s*(//|\*|/\*)")


def strip_block_comments(lines: list[str]) -> list[str]:
    out, in_block = [], False
    for line in lines:
        if in_block:
            if "*/" in line:
                in_block = False
            out.append("")
            continue
        if line.lstrip().startswith("/*"):
            if "*/" not in line:
                in_block = True
            out.append("")
            continue
        out.append(line)
    return out


def check_file(path: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        return [f"cannot read: {exc}"], []

    lines = strip_block_comments(raw.splitlines())

    if not DEFAULT_EXPORT_RE.search(raw):
        errors.append("no default export factory found (Pi calls `export default function (pi: ExtensionAPI)`)")
    elif not EXT_API_RE.search(raw):
        warnings.append("default export exists but ExtensionAPI is never referenced — is this a Pi extension?")

    for i, line in enumerate(lines, 1):
        if CODE_FENCE_RE.match(line):
            continue
        # Module-scope side effects: the call starts at column 0 (or follows `const x =` at column 0).
        if SIDE_EFFECT_RE.search(line) and not line.startswith(("\t", " ", "}", ")")):
            errors.append(
                f"line {i}: side effect at module scope — start processes/timers/watchers from "
                f"session_start or lazily, not at load time: {line.strip()[:80]}"
            )
        if CONTINUE_RE.search(line):
            warnings.append(
                f"line {i}: `continue: true` — verify the continuation condition is guarded or it loops forever"
            )
        if CONSOLE_RE.search(line):
            warnings.append(f"line {i}: leftover console.log/debug — use ctx.ui.notify or remove")

    if DIALOG_RE.search(raw) and not HASUI_GUARD_RE.search(raw):
        warnings.append("dialogs (confirm/select/prompt) used without any ctx.hasUI guard — breaks in json/print modes")
    if CUSTOM_UI_RE.search(raw) and not TUI_GUARD_RE.search(raw):
        warnings.append("custom terminal UI used without a ctx.mode === \"tui\" guard — only tui mode renders components")

    if re.search(r"registerCommand\s*\(", raw) and not re.search(r"handler\s*:", raw):
        errors.append("registerCommand without a handler")
    if re.search(r"registerTool\s*\(", raw) and not re.search(r"execute\s*[:(]", raw):
        warnings.append("registerTool without a visible execute() — check the tool definition")
    return errors, warnings


def check_package(pkg_dir: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    pj = os.path.join(pkg_dir, "package.json")
    try:
        with open(pj, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"package.json unreadable: {exc}"], []

    if "pi-package" not in data.get("keywords", []):
        warnings.append("package.json keywords missing 'pi-package' (needed for package discovery)")
    pi_manifest = data.get("pi", {})
    ext_paths = pi_manifest.get("extensions", [])
    if isinstance(ext_paths, str):
        ext_paths = [ext_paths]
    for p in ext_paths:
        clean = p.lstrip("./")
        if "*" in clean:
            continue
        if not os.path.exists(os.path.join(pkg_dir, clean)):
            errors.append(f"pi.extensions path '{p}' does not exist")
    if not ext_paths and not os.path.isdir(os.path.join(pkg_dir, "extensions")):
        warnings.append("no pi.extensions manifest and no extensions/ directory")
    deps = data.get("dependencies", {})
    for pi_pkg in ("@earendil-works/pi-coding-agent", "@earendil-works/pi-ai", "@earendil-works/pi-tui", "typebox"):
        if pi_pkg in deps:
            warnings.append(f"'{pi_pkg}' is in dependencies — Pi supplies it; use peerDependencies instead")
    return errors, warnings


def collect(path: str) -> tuple[list[str], list[str]]:
    """Return (extension_files, package_dirs) under path."""
    files, pkg_dirs = [], []
    if os.path.isfile(path):
        if path.endswith((".ts", ".js", ".mts", ".mjs")):
            files.append(path)
        elif os.path.basename(path) == "package.json":
            pkg_dirs.append(os.path.dirname(path))
        return files, pkg_dirs
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", "dist", ".git") and not d.startswith(".")]
        if "package.json" in filenames:
            pkg_dirs.append(dirpath)
        for f in filenames:
            if f.endswith((".ts", ".js", ".mts", ".mjs")) and not f.endswith(".d.ts"):
                files.append(os.path.join(dirpath, f))
    return sorted(files), sorted(pkg_dirs)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    failed = False
    seen = False
    for root in argv[1:]:
        if not os.path.exists(root):
            print(f"{root}: no such file or directory")
            return 2
        files, pkg_dirs = collect(root)
        for pkg in pkg_dirs:
            seen = True
            errors, warnings = check_package(pkg)
            report(os.path.join(pkg, "package.json"), errors, warnings)
            failed = failed or bool(errors)
        for f in files:
            seen = True
            errors, warnings = check_file(f)
            report(f, errors, warnings)
            failed = failed or bool(errors)
    if not seen:
        print("nothing to check (no .ts/.js files or package.json found)")
        return 2
    return 1 if failed else 0


def report(path: str, errors: list[str], warnings: list[str]) -> None:
    rel = os.path.relpath(path)
    if not errors and not warnings:
        print(f"OK    {rel}")
        return
    print(f"{'ERROR' if errors else 'WARN '} {rel}")
    for e in errors:
        print(f"        error:   {e}")
    for w in warnings:
        print(f"        warning: {w}")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
