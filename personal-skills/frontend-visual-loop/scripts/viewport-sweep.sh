#!/usr/bin/env bash
# viewport-sweep.sh — capture one page at mobile/tablet/desktop plus console + page errors.
#
# Usage: viewport-sweep.sh <url> <output-dir> [width:height ...]
#   viewport-sweep.sh http://localhost:5173/ ./.ui-checks
#   viewport-sweep.sh http://localhost:5173/ ./.ui-checks 1440:900 320:568
#
# Requires: agent-browser (>= 0.35) on PATH, with a browser installed via
#   `agent-browser install --with-deps`.
# Writes <output-dir>/<name>.png for each viewport and prints captured console and
# error output. Screenshots are returned to the caller as file paths only — read the
# PNGs afterwards to actually inspect them.

set -uo pipefail

usage() {
  echo "usage: $0 <url> <output-dir> [width:height ...]" >&2
  exit 2
}

[ $# -ge 2 ] || usage
URL="$1"
OUT_DIR="$2"

command -v agent-browser >/dev/null 2>&1 || {
  echo "agent-browser not on PATH. Install: npm install -g agent-browser && agent-browser install --with-deps" >&2
  exit 1
}

# Resolve the output directory to an absolute path before handing it to the browser:
# the agent-browser daemon keeps the cwd it was launched with, so relative paths can
# land somewhere other than this script's directory.
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"

if [ $# -ge 3 ]; then
  shift 2
  VIEWPORTS=("$@")
  NAMES=()
  for vp in "${VIEWPORTS[@]}"; do NAMES+=("custom-${vp//:/x}"); done
else
  VIEWPORTS=("390:844" "768:1024" "1280:800")
  NAMES=("mobile" "tablet" "desktop")
fi

# Confirm the target answers before screenshotting; a dead dev server produces a blank
# page that looks like a rendering bug.
CODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$URL" 2>/dev/null)"
CODE="${CODE:-000}"
case "$CODE" in
  2*) echo "target: $URL (HTTP $CODE)" ;;
  *)  echo "WARNING: $URL returned HTTP $CODE — screenshots may show an error page, not your UI." >&2 ;;
esac

# Navigate once before resizing. Without this the browser captures whatever page it
# already had open, which yields plausible-looking screenshots of the wrong UI and an
# empty console.
if ! agent-browser open "$URL" >/dev/null 2>&1; then
  echo "FAILED: could not open $URL in the browser" >&2
  exit 1
fi

# Confirm this browser instance really holds the page. When stale daemons from other
# directories are alive, `open` and `screenshot` can land on different browsers and you
# get an all-white PNG that looks like a broken app rather than a broken session.
LOADED="$(agent-browser get url 2>/dev/null | tail -1)"
if [ -z "$LOADED" ] || [ "$LOADED" = "about:blank" ]; then
  cat >&2 <<'FIX'
FAILED: browser reports about:blank immediately after a successful open.
A stale agent-browser daemon is probably hijacking the session. Clear it:
  agent-browser close --all
  pkill -f 'agent-[b]rowser-linux'
  agent-browser doctor
FIX
  exit 1
fi

fail=0
for i in "${!VIEWPORTS[@]}"; do
  vp="${VIEWPORTS[$i]}"
  name="${NAMES[$i]}"
  w="${vp%%:*}"
  h="${vp##*:}"
  shot="$OUT_DIR/$name.png"

  if agent-browser set viewport "$w" "$h" >/dev/null 2>&1 \
     && agent-browser wait 500 >/dev/null 2>&1 \
     && agent-browser screenshot "$shot" >/dev/null 2>&1 \
     && [ -s "$shot" ]; then
    echo "captured: $shot (${w}x${h}, $(wc -c <"$shot") bytes)"
  else
    echo "FAILED: ${name} (${w}x${h}) — no screenshot written to $shot" >&2
    fail=1
  fi
done

echo "--- console ---"
agent-browser console 2>&1 || echo "(console unavailable)"

echo "--- page errors (json) ---"
# --json because plain `errors` renders a bare marker for multi-line stack traces.
agent-browser errors --json 2>&1 || echo "(errors unavailable)"

exit "$fail"
