#!/usr/bin/env python3
"""Validate Agent Skills directories for Pi.

Usage:
    python3 validate_skill.py <skill-dir-or-parent-dir> [...]

Checks each directory containing a SKILL.md (searched recursively):
  - frontmatter present and parseable
  - required fields: name, description
  - field constraints from the Agent Skills specification
  - name matches parent directory name
  - body size guidance (<500 lines)
  - relative file references in the body resolve to real files

Exit code 0 = all skills valid (warnings allowed), 1 = at least one error.
Stdlib only; uses PyYAML when available and falls back to a minimal parser.
"""

from __future__ import annotations

import os
import re
import sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500
MAX_BODY_LINES = 500
KNOWN_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
    "disable-model-invocation",
}
# Markdown references that should point at bundled files: `path` in backticks
# containing a file extension and no spaces/scheme.
REF_RE = re.compile(r"`([^`\s]+\.(?:md|py|sh|js|ts|json|ya?ml|txt|csv|html))`")


def parse_frontmatter(text: str):
    """Return (frontmatter_dict_or_None, body, error_or_None)."""
    if not text.startswith("---"):
        return None, text, "SKILL.md does not start with '---' frontmatter"
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", text, re.DOTALL)
    if not m:
        return None, text, "unterminated frontmatter (missing closing '---')"
    raw, body = m.group(1), text[m.end():]
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(raw)
        if data is None:
            data = {}
        if not isinstance(data, dict):
            return None, body, "frontmatter is not a mapping"
        return data, body, None
    except ImportError:
        pass
    except Exception as exc:  # noqa: BLE001
        return None, body, f"frontmatter YAML failed to parse: {exc}"
    return _parse_frontmatter_fallback(raw), body, None


def _parse_frontmatter_fallback(raw: str):
    """Minimal 'key: value' parser used when PyYAML is unavailable."""
    data: dict = {}
    current_key = None
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            if value:
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                data[key] = value
                current_key = None
            else:
                data[key] = {}
                current_key = key
            continue
        m = re.match(r"^\s+([A-Za-z0-9_.-]+):\s*(.*)$", line)
        if m and current_key and isinstance(data.get(current_key), dict):
            data[current_key][m.group(1)] = m.group(2).strip()
    return data


def find_skills(root: str) -> list[str]:
    """Return SKILL.md paths under root (root itself included if it is a skill)."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "node_modules"]
        if "SKILL.md" in filenames:
            found.append(os.path.join(dirpath, "SKILL.md"))
    return sorted(found)


def validate(skill_md: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_dir = os.path.dirname(skill_md)
    dir_name = os.path.basename(skill_dir)

    try:
        with open(skill_md, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return [f"cannot read: {exc}"], []

    data, body, err = parse_frontmatter(text)
    if err:
        errors.append(err)
        return errors, warnings
    assert data is not None

    # name
    name = data.get("name")
    if not name:
        errors.append("missing required field 'name'")
    elif not isinstance(name, str):
        errors.append("'name' must be a string")
    else:
        if not NAME_RE.match(name):
            errors.append(
                f"invalid name '{name}': lowercase letters, numbers, and single hyphens only, "
                "no leading/trailing hyphen"
            )
        if len(name) > MAX_NAME:
            errors.append(f"name exceeds {MAX_NAME} characters ({len(name)})")
        if name != dir_name:
            warnings.append(
                f"name '{name}' does not match directory '{dir_name}' "
                "(Pi tolerates this; other Agent Skills implementations may not)"
            )

    # description
    desc = data.get("description")
    if not desc:
        errors.append("missing required field 'description' (skill will not load)")
    elif not isinstance(desc, str):
        errors.append("'description' must be a string")
    else:
        if len(desc) > MAX_DESCRIPTION:
            errors.append(f"description exceeds {MAX_DESCRIPTION} characters ({len(desc)})")
        low = desc.lower()
        if "use when" not in low and "use this" not in low and "trigger" not in low:
            warnings.append(
                "description does not say when to use the skill; add explicit trigger cues "
                "('Use when the user ...') so Pi routes to it"
            )
        if len(desc) < 40:
            warnings.append("description is very short; it is the only routing signal Pi sees at startup")

    # compatibility
    compat = data.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            errors.append("'compatibility' must be a string")
        elif len(compat) > MAX_COMPATIBILITY:
            errors.append(f"compatibility exceeds {MAX_COMPATIBILITY} characters ({len(compat)})")

    # metadata
    meta = data.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        errors.append("'metadata' must be a mapping")
    elif isinstance(meta, dict):
        for k, v in meta.items():
            if not isinstance(k, str) or not isinstance(v, str):
                warnings.append(f"metadata['{k}'] should be a string value (spec: string->string)")

    # allowed-tools
    tools = data.get("allowed-tools")
    if tools is not None and not isinstance(tools, str):
        errors.append("'allowed-tools' must be a space-separated string")

    # disable-model-invocation
    dmi = data.get("disable-model-invocation")
    if dmi is not None and not isinstance(dmi, bool) and str(dmi).lower() not in {"true", "false"}:
        errors.append("'disable-model-invocation' must be a boolean")

    # unknown fields
    for key in data:
        if key not in KNOWN_FIELDS:
            warnings.append(f"unknown frontmatter field '{key}' (ignored; put extras under 'metadata')")

    # body checks
    lines = body.count("\n") + (1 if body.strip() else 0)
    if not body.strip():
        errors.append("SKILL.md body is empty")
    elif lines > MAX_BODY_LINES:
        warnings.append(
            f"body is {lines} lines (> {MAX_BODY_LINES}); move detail into references/*.md "
            "with pointers from the body"
        )

    # bundled file references
    for ref in set(REF_RE.findall(body)):
        if ref.startswith(("http://", "https://", "/", "~")) or "://" in ref:
            continue
        if "<" in ref or ">" in ref:  # placeholder like <skill-dir>/scripts/x.py
            continue
        if "*" in ref or "?" in ref:  # glob in prose, not a specific file
            continue
        candidate = os.path.normpath(os.path.join(skill_dir, ref))
        # Only skill-local prefixes are held to account; other relative paths
        # usually mean project files (docs/, src/) that are not bundled here.
        if not re.match(r"^(scripts|references|assets|evals)/", ref):
            continue
        if not os.path.exists(candidate):
            errors.append(f"broken reference: '{ref}' does not exist in the skill directory")

    return errors, warnings


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    paths: list[str] = []
    for root in argv[1:]:
        if os.path.isfile(root) and os.path.basename(root) == "SKILL.md":
            paths.append(root)
        elif os.path.isdir(root):
            found = find_skills(root)
            if not found:
                print(f"{root}: no SKILL.md found (searched recursively)")
            paths.extend(found)
        else:
            print(f"{root}: not a file or directory")
            return 2

    failed = False
    for skill_md in paths:
        rel = os.path.relpath(skill_md)
        errors, warnings = validate(skill_md)
        if not errors and not warnings:
            print(f"OK    {rel}")
            continue
        status = "ERROR" if errors else "WARN "
        print(f"{status} {rel}")
        for e in errors:
            print(f"        error:   {e}")
        for w in warnings:
            print(f"        warning: {w}")
        if errors:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
